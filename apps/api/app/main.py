from contextlib import asynccontextmanager
from uuid import uuid4

from fastapi import FastAPI, HTTPException, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api import api_v1_router
from app.core.config import get_settings
from app.core.errors import AppError
from app.core.logging import configure_logging
from app.db.base import Base
from app.db.session import SessionLocal, engine
from app.schemas.common import ErrorDetail, ErrorResponse
from app.services import ensure_seed_data

settings = get_settings()
configure_logging()


@asynccontextmanager
async def lifespan(_: FastAPI):
    Base.metadata.create_all(bind=engine)
    with SessionLocal() as db:
        ensure_seed_data(db)
    yield


app = FastAPI(title=settings.app_name, version="0.1.0", lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def add_trace_id(request: Request, call_next):
    trace_id = request.headers.get("x-trace-id") or uuid4().hex
    request.state.trace_id = trace_id
    response = await call_next(request)
    response.headers["x-trace-id"] = trace_id
    return response


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    trace_id = getattr(request.state, "trace_id", uuid4().hex)
    payload = ErrorResponse(
        error=ErrorDetail(
            code=f"HTTP_{exc.status_code}",
            message=str(exc.detail),
            trace_id=trace_id,
            details={},
        )
    )
    return JSONResponse(status_code=exc.status_code, content=payload.model_dump())


@app.exception_handler(AppError)
async def app_error_handler(request: Request, exc: AppError):
    trace_id = getattr(request.state, "trace_id", uuid4().hex)
    payload = ErrorResponse(
        error=ErrorDetail(
            code=exc.code,
            message=exc.message,
            trace_id=trace_id,
            details=exc.details,
        )
    )
    return JSONResponse(status_code=exc.status_code, content=payload.model_dump())


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    trace_id = getattr(request.state, "trace_id", uuid4().hex)
    payload = ErrorResponse(
        error=ErrorDetail(
            code="VALIDATION_ERROR",
            message="Request validation failed",
            trace_id=trace_id,
            details={"errors": exc.errors()},
        )
    )
    return JSONResponse(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, content=payload.model_dump())


@app.exception_handler(ValueError)
async def value_error_handler(request: Request, exc: ValueError):
    trace_id = getattr(request.state, "trace_id", uuid4().hex)
    payload = ErrorResponse(
        error=ErrorDetail(
            code="BAD_REQUEST",
            message=str(exc),
            trace_id=trace_id,
            details={},
        )
    )
    return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content=payload.model_dump())


@app.get("/health")
def health() -> dict:
    from datetime import datetime, timezone
    from app.services.provider import OllamaProvider

    provider = OllamaProvider()
    provider_health = provider.health_check()

    return {
        "status": "ok",
        "service": settings.app_name,
        "time": datetime.now(timezone.utc).isoformat(),
        "checks": {
            "db": "ok",
            "provider": provider_health.get("status", "unknown"),
        },
        "provider": {
            "mode": provider_health.get("mode", "unknown"),
            "status": provider_health.get("status", "unknown"),
            "model": provider_health.get("model", "unknown"),
            "version": provider_health.get("version", "unknown"),
            "chat_model_available": provider_health.get("chat_model_available", False),
            "message": provider_health.get("message"),
        },
    }


@app.get("/metrics")
def metrics() -> dict:
    """Basic metrics endpoint — request counts, DB size, provider status."""
    import os
    from app.services.provider import OllamaProvider

    db_path = settings.database_url.replace("sqlite:///", "")
    db_size_mb = 0.0
    try:
        if os.path.exists(db_path):
            db_size_mb = round(os.path.getsize(db_path) / (1024 * 1024), 2)
    except OSError:
        pass

    provider = OllamaProvider()
    provider_health = provider.health_check()

    return {
        "status": "ok",
        "metrics": {
            "version": "0.1.0",
            "env": settings.app_env,
            "db_size_mb": db_size_mb,
            "provider_status": provider_health.get("status", "unknown"),
            "provider_mode": provider_health.get("mode", "unknown"),
            "provider_model": provider_health.get("model", "unknown"),
            "provider_version": provider_health.get("version", "unknown"),
            "provider_chat_model_available": provider_health.get("chat_model_available", False),
            "provider_message": provider_health.get("message"),
        },
    }


app.include_router(api_v1_router, prefix=settings.api_v1_prefix)
