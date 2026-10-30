"""Safe and consistent API errors; never include SQL, tokens or patient input."""

import logging

from fastapi import Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from sqlalchemy.exc import IntegrityError
from starlette.exceptions import HTTPException

logger = logging.getLogger(__name__)


class DomainError(Exception):
    def __init__(self, status: int, code: str, message: str):
        self.status, self.code, self.message = status, code, message


def require(condition, message="This action is not permitted.", status=403, code="FORBIDDEN"):
    if not condition:
        raise DomainError(status, code, message)


def install_handlers(app):
    def response(request, status, code, message, fields=None):
        return JSONResponse(
            status_code=status,
            content={
                "code": code,
                "message": message,
                "field_errors": fields or {},
                "request_id": request.state.request_id,
            },
            headers={"Retry-After": "60"} if status == 429 else {},
        )

    @app.exception_handler(DomainError)
    async def domain_error(request: Request, exc: DomainError):
        return response(request, exc.status, exc.code, exc.message)

    @app.exception_handler(RequestValidationError)
    async def validation_error(request: Request, exc: RequestValidationError):
        fields = {".".join(map(str, e["loc"][1:])): [e["msg"]] for e in exc.errors()}
        return response(
            request, 422, "VALIDATION_ERROR", "Please check the highlighted fields.", fields
        )

    @app.exception_handler(IntegrityError)
    async def integrity_error(request: Request, exc: IntegrityError):
        return response(
            request, 409, "CONFLICT", "The record changed or already exists. Refresh and retry."
        )

    @app.exception_handler(HTTPException)
    async def http_error(request: Request, exc: HTTPException):
        return response(request, exc.status_code, "HTTP_ERROR", str(exc.detail))

    @app.exception_handler(Exception)
    async def unexpected_error(request: Request, exc: Exception):
        # Log the class and correlation ID only; exception strings may contain clinical data.
        logger.error(
            "Unexpected error %s request_id=%s", type(exc).__name__, request.state.request_id
        )
        return response(request, 500, "INTERNAL_ERROR", "An unexpected error occurred.")
