"""Application lifecycle owns API connections; migrations and workers run separately."""

from contextlib import asynccontextmanager
from uuid import uuid4

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from redis.exceptions import RedisError
from sqlalchemy.exc import SQLAlchemyError

from app.api.router import api_router
from app.core.config import settings
from app.core.errors import DomainError, install_handlers
from app.core.redis import create_redis
from app.database.session import check_database_connection, close_db
from app.modules.fhir.router import router as fhir_router


@asynccontextmanager
async def lifespan(app):
    app.state.redis = create_redis()
    try:
        yield
    finally:
        await app.state.redis.aclose()
        await close_db()


app = FastAPI(
    title=settings.app_name,
    version="0.2.0",
    debug=False,
    lifespan=lifespan,
    description="MediLink asynchronous REST API with Redis and Celery.",
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=False,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE"],
    allow_headers=["Accept", "Authorization", "Content-Type", "Idempotency-Key", "X-Request-ID"],
    expose_headers=["X-Request-ID", "Retry-After"],
    max_age=600,
)
install_handlers(app)


@app.middleware("http")
async def request_context(request: Request, call_next):
    # Generate our own correlation ID; do not reflect untrusted headers into logs.
    request.state.request_id = str(uuid4())
    response = await call_next(request)
    response.headers["X-Request-ID"] = request.state.request_id
    response.headers["Cache-Control"] = "no-store"
    response.headers["X-Content-Type-Options"] = "nosniff"
    return response


app.include_router(api_router, prefix=settings.api_v1_prefix)
app.include_router(fhir_router)


@app.get("/health", tags=["health"])
async def health_check():
    return {"status": "ok"}


@app.get("/health/ready", tags=["health"])
async def ready(request: Request):
    try:
        await check_database_connection()
        await request.app.state.redis.ping()
    except (RedisError, SQLAlchemyError, OSError) as exc:
        raise DomainError(503, "NOT_READY", "A required service is unavailable.") from exc
    return {"status": "ready"}
