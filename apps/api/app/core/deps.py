from collections.abc import Generator

from fastapi import Depends, Header, Request
from sqlalchemy.orm import Session

from app.core.errors import AppError
from app.core.security import decode_token
from app.db.session import SessionLocal
from app.models.models import User
from app.services.auth import AuthService


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_trace_id(request: Request) -> str:
    return getattr(request.state, "trace_id", "-")


def get_current_user(
    authorization: str | None = Header(default=None),
    db: Session = Depends(get_db),
) -> User:
    if not authorization or not authorization.startswith("Bearer "):
        raise AppError(code="UNAUTHORIZED", message="Missing bearer token", status_code=401)

    token = authorization.split(" ", 1)[1]
    try:
        payload = decode_token(token)
    except ValueError as exc:
        raise AppError(code="UNAUTHORIZED", message="Invalid token", status_code=401) from exc
    if payload.get("type") != "access":
        raise AppError(code="UNAUTHORIZED", message="Invalid token type", status_code=401)
    if AuthService.is_token_revoked(db, payload.get("jti")):
        raise AppError(code="UNAUTHORIZED", message="Token revoked", status_code=401)

    user = db.get(User, payload.get("sub"))
    if not user:
        raise AppError(code="UNAUTHORIZED", message="User not found", status_code=401)
    return user
