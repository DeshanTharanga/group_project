"""Firebase verifies humans; local roles, status and approvals authorize every request."""

import asyncio
import hashlib
from dataclasses import dataclass
from uuid import UUID

from fastapi import Depends, Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from firebase_admin import auth, get_app, initialize_app
from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.errors import DomainError, require
from app.core.redis import rate_limit
from app.database.session import get_session
from app.modules.identity.models import Role, User, UserRole
from app.modules.integrations.models import IntegrationClient

bearer = HTTPBearer(auto_error=False)


def digest(value: str) -> str:
    return hashlib.sha256(value.encode()).hexdigest()


def verify_token(token):
    try:
        get_app()
    except ValueError:
        initialize_app(
            options={"projectId": settings.firebase_project_id}
            if settings.firebase_project_id
            else None
        )
    return auth.verify_id_token(token, check_revoked=True)


async def firebase_identity(
    request: Request, credentials: HTTPAuthorizationCredentials | None = Depends(bearer)
):
    require(credentials is not None, "A Firebase ID token is required.", 401, "UNAUTHENTICATED")
    await rate_limit(request.app.state.redis, request.client.host if request.client else "unknown")
    try:
        return await asyncio.to_thread(verify_token, credentials.credentials)
    except Exception as exc:
        raise DomainError(
            401, "INVALID_TOKEN", "The identity token is invalid or expired."
        ) from exc


@dataclass
class Context:
    session: AsyncSession
    request: Request
    user: User | None
    roles: set[str]
    identity: dict
    client: IntegrationClient | None = None

    @property
    def actor_id(self) -> UUID:
        return self.client.id if self.client is not None else self.user.id

    @property
    def actor_type(self):
        return "client" if self.client is not None else "user"

    def admin(self, super_only=False):
        require(bool(self.roles & ({"super_admin"} if super_only else {"admin", "super_admin"})))

    def own(self, user_id):
        require(self.user is not None and self.user.id == user_id)


async def context(
    request: Request, identity=Depends(firebase_identity), session=Depends(get_session)
):
    # Serialize mutations by the verified actor before acquiring any business row locks.
    # The shared account lock then permits cross-actor consent/claim checks without deadlocks.
    if request.method != "GET":
        actor_lock = int.from_bytes(
            hashlib.sha256(("actor:" + identity["uid"]).encode()).digest()[:8], "big", signed=True
        )
        await session.execute(text("SELECT pg_advisory_xact_lock(:key)"), {"key": actor_lock})
    # Account suspension and role changes need an exclusive lock on this row.
    user = await session.scalar(
        select(User).where(User.firebase_uid == identity["uid"]).with_for_update(read=True)
    )
    require(user is not None, "Complete onboarding first.", 403, "ONBOARDING_REQUIRED")
    require(user.status == "active", "This account is not active.")
    roles = set(
        await session.scalars(
            select(Role.code)
            .join(UserRole, UserRole.role_id == Role.id)
            .where(UserRole.user_id == user.id)
        )
    )
    return Context(session, request, user, roles, identity)


async def onboarding_context(
    request: Request, identity=Depends(firebase_identity), session=Depends(get_session)
):
    return Context(session, request, None, set(), identity)


async def integration_context(request: Request, session=Depends(get_session)):
    from app.services.common import now

    key = request.headers.get("X-API-Key", "")
    require(bool(key), "An integration key is required.", 401, "UNAUTHENTICATED")
    await rate_limit(request.app.state.redis, request.client.host if request.client else "unknown")
    client = await session.scalar(
        select(IntegrationClient)
        .where(IntegrationClient.credential_hash == digest(key))
        .with_for_update(read=True)
    )
    require(client is not None, "Invalid integration key.", 401, "UNAUTHENTICATED")
    require(
        client.status == "active"
        and client.expires_at > now()
        and client.scopes == ["reports:write"]
    )
    return Context(session, request, None, set(), {}, client)
