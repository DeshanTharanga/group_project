from datetime import UTC, datetime
from types import SimpleNamespace
from unittest.mock import AsyncMock
from uuid import uuid4

import pytest

from app.core.errors import DomainError
from app.core.security import Context
from app.modules.audit.service import privileged
from app.services.common import patient_access, professional


def context(roles):
    return Context(AsyncMock(), SimpleNamespace(), SimpleNamespace(id=uuid4()), set(roles), {})


async def test_admin_role_does_not_imply_doctor_access():
    ctx = context(["admin"])
    with pytest.raises(DomainError) as exc:
        await professional(ctx)
    assert exc.value.status == 403
    ctx.session.scalar.assert_not_awaited()


def test_privileged_actions_require_recent_mfa():
    ctx = context(["super_admin"])
    with pytest.raises(DomainError) as exc:
        privileged(ctx)
    assert exc.value.code == "MFA_REQUIRED"
    ctx.identity = {
        "auth_time": datetime.now(UTC).timestamp(),
        "firebase": {"sign_in_second_factor": "totp"},
    }
    privileged(ctx)
    ctx.identity["auth_time"] = 0
    with pytest.raises(DomainError):
        privileged(ctx)


async def test_cannot_claim_own_consultation_as_patient(monkeypatch):
    ctx = context(["patient"])
    monkeypatch.setattr("app.services.common.get", AsyncMock())
    with pytest.raises(DomainError) as exc:
        await patient_access(ctx, ctx.user.id, "prescriptions", uuid4())
    assert exc.value.status == 422
