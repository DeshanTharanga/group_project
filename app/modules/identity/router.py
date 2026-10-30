"""Thin async HTTP routes. Domain services own permissions and state transitions."""

from typing import Annotated

from fastapi import APIRouter, Depends, Request

from app.core.security import Context, context, onboarding_context
from app.modules.identity import schemas as s
from app.modules.identity import service
from app.services.common import invoke

router = APIRouter()


@router.post("/me/onboard", tags=["Identity"], status_code=200, response_model=s.OnboardResponse)
async def onboard(
    request: Request, ctx: Annotated[Context, Depends(onboarding_context)], data: s.OnboardInput
):
    result = await invoke(
        ctx,
        "onboard",
        service.onboard,
        data.model_dump(exclude_unset=True),
        params={},
        response_model=s.OnboardResponse,
        status=200,
        idempotent=False,
    )
    return result


@router.get("/me", tags=["Identity"], status_code=200, response_model=s.MeResponse)
async def me(request: Request, ctx: Annotated[Context, Depends(context)]):
    result = await invoke(
        ctx,
        "me",
        service.me,
        None,
        params={},
        response_model=s.MeResponse,
        status=200,
        idempotent=False,
    )
    return result


@router.patch("/me", tags=["Identity"], status_code=200, response_model=s.UpdateMeResponse)
async def update_me(
    request: Request, ctx: Annotated[Context, Depends(context)], data: s.UpdateMeInput
):
    result = await invoke(
        ctx,
        "update_me",
        service.update_me,
        data.model_dump(exclude_unset=True),
        params={},
        response_model=s.UpdateMeResponse,
        status=200,
        idempotent=False,
    )
    return result


@router.patch(
    "/me/patient-profile",
    tags=["Identity"],
    status_code=200,
    response_model=s.UpdatePatientProfileResponse,
)
async def update_patient_profile(
    request: Request, ctx: Annotated[Context, Depends(context)], data: s.UpdatePatientProfileInput
):
    result = await invoke(
        ctx,
        "update_patient_profile",
        service.update_patient_profile,
        data.model_dump(exclude_unset=True),
        params={},
        response_model=s.UpdatePatientProfileResponse,
        status=200,
        idempotent=False,
    )
    return result


@router.put(
    "/me/professional-profile",
    tags=["Identity"],
    status_code=200,
    response_model=s.UpdateProfessionalProfileResponse,
)
async def update_professional_profile(
    request: Request,
    ctx: Annotated[Context, Depends(context)],
    data: s.UpdateProfessionalProfileInput,
):
    result = await invoke(
        ctx,
        "update_professional_profile",
        service.update_professional_profile,
        data.model_dump(exclude_unset=True),
        params={},
        response_model=s.UpdateProfessionalProfileResponse,
        status=200,
        idempotent=False,
    )
    return result
