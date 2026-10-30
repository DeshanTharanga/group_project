"""Integration tests use only synthetic data in an explicitly supplied disposable database."""

import os
from datetime import date
from types import SimpleNamespace
from uuid import uuid4

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from app.core.security import firebase_identity
from app.database import models as m
from app.database.session import get_session
from app.main import app


@pytest.fixture
async def api(tmp_path, monkeypatch):
    url = os.getenv("TEST_DATABASE_URL")
    if not url:
        pytest.skip("Set TEST_DATABASE_URL to a disposable migrated PostgreSQL database.")
    from app.core.config import settings

    monkeypatch.setattr(settings, "private_upload_dir", str(tmp_path))
    engine = create_async_engine(url, pool_pre_ping=True)
    sessions = async_sessionmaker(engine, expire_on_commit=False, autoflush=False)
    users = {}
    references = {}
    orgs = {}
    async with sessions() as session:
        async with session.begin():
            for role in ("patient", "doctor", "pharmacist", "lab_staff", "admin", "super_admin"):
                role_obj = await session.scalar(select(m.Role).where(m.Role.code == role))
                user = m.User(
                    firebase_uid=f"test-{uuid4()}",
                    display_name=f"Synthetic {role}",
                    status="active",
                )
                session.add(user)
                await session.flush()
                users[role] = user
                session.add(m.UserRole(user_id=user.id, role_id=role_obj.id))
                if role == "patient":
                    session.add(
                        m.PatientProfile(
                            user_id=user.id, date_of_birth=date(2000, 1, 1), sex="female"
                        )
                    )
                if role in ("doctor", "pharmacist", "lab_staff"):
                    reference = uuid4().hex if role == "doctor" else None
                    references[role] = reference
                    session.add(
                        m.ProfessionalProfile(
                            user_id=user.id,
                            role=role,
                            doctor_reference=reference,
                            verification_status="approved",
                            registration_number="SYNTHETIC",
                        )
                    )
                if role in ("pharmacist", "lab_staff"):
                    org = m.Organization(
                        name="Synthetic organization",
                        type="pharmacy" if role == "pharmacist" else "laboratory",
                        status="active",
                    )
                    session.add(org)
                    await session.flush()
                    orgs[role] = org
                    session.add(
                        m.OrganizationMembership(
                            organization_id=org.id, user_id=user.id, role=role, status="approved"
                        )
                    )

    async def session_override():
        async with sessions() as session:
            try:
                yield session
            finally:
                for path in session.info.pop("new_files", []):
                    path.unlink(missing_ok=True)

    async def identity_override(request):
        # Request typing is added explicitly below so FastAPI treats it as a Request, not a query.
        role = request.headers.get("X-Test-Role", "patient")
        return {
            "uid": users[role].firebase_uid,
            "auth_time": __import__("time").time(),
            "firebase": {"sign_in_second_factor": "totp"},
        }

    from fastapi import Request

    identity_override.__annotations__["request"] = Request
    app.dependency_overrides[get_session] = session_override
    app.dependency_overrides[firebase_identity] = identity_override
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:

        async def call(method, path, role="patient", **kwargs):
            headers = kwargs.pop("headers", {})
            return await client.request(
                method, path, headers={"X-Test-Role": role, **headers}, **kwargs
            )

        yield SimpleNamespace(
            call=call, users=users, orgs=orgs, references=references, sessions=sessions
        )
    app.dependency_overrides.clear()
    await engine.dispose()
