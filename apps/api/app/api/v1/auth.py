from fastapi import APIRouter, Depends, Header, status
from sqlalchemy.orm import Session

from app.core.deps import get_current_user, get_db, get_trace_id
from app.core.errors import AppError
from app.models.models import User
from app.schemas.common import LoginRequest, LoginResponse, LogoutRequest, RefreshRequest, RegisterRequest, UserResponse
from app.services.audit import AuditService
from app.services.auth import AuthService

router = APIRouter()


@router.post("/login", response_model=LoginResponse)
def login(payload: LoginRequest, db: Session = Depends(get_db), trace_id: str = Depends(get_trace_id)) -> LoginResponse:
    tokens = AuthService.login(db, payload.email, payload.password)
    if not tokens:
        AuditService.append(
            db,
            trace_id=trace_id,
            actor=payload.email,
            action="auth_login",
            resource_type="user",
            resource_id="-",
            result="unauthorized",
            request_summary="login_failed",
        )
        raise AppError(code="UNAUTHORIZED", message="Invalid email or password", status_code=status.HTTP_401_UNAUTHORIZED)
    access_token, refresh_token, user = tokens
    AuditService.append(
        db,
        trace_id=trace_id,
        actor=user.email,
        action="auth_login",
        resource_type="user",
        resource_id=user.id,
        result="success",
        request_summary="login_success",
    )
    return LoginResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        user=UserResponse.model_validate(user),
        trace_id=trace_id,
    )


@router.post("/refresh", response_model=LoginResponse)
def refresh(payload: RefreshRequest, db: Session = Depends(get_db), trace_id: str = Depends(get_trace_id)) -> LoginResponse:
    tokens = AuthService.refresh(db, payload.refresh_token)
    if not tokens:
        AuditService.append(
            db,
            trace_id=trace_id,
            actor="anonymous",
            action="auth_refresh",
            resource_type="user",
            resource_id="-",
            result="unauthorized",
            request_summary="refresh_failed",
        )
        raise AppError(code="UNAUTHORIZED", message="Invalid refresh token", status_code=status.HTTP_401_UNAUTHORIZED)
    access_token, refresh_token, user = tokens
    AuditService.append(
        db,
        trace_id=trace_id,
        actor=user.email,
        action="auth_refresh",
        resource_type="user",
        resource_id=user.id,
        result="success",
        request_summary="refresh_success",
    )
    return LoginResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        user=UserResponse.model_validate(user),
        trace_id=trace_id,
    )


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
def logout(
    payload: LogoutRequest,
    db: Session = Depends(get_db),
    trace_id: str = Depends(get_trace_id),
    authorization: str | None = Header(default=None),
) -> None:
    access_revocation = None
    refresh_revocation = None

    if authorization and authorization.startswith("Bearer "):
        access_revocation = AuthService.revoke_token(db, authorization.split(" ", 1)[1], token_type="access")
    if payload.refresh_token:
        refresh_revocation = AuthService.revoke_token(db, payload.refresh_token, token_type="refresh")

    user = (access_revocation.user if access_revocation else None) or (refresh_revocation.user if refresh_revocation else None)
    revoked = (access_revocation.revoked if access_revocation else False) or (refresh_revocation.revoked if refresh_revocation else False)
    AuditService.append(
        db,
        trace_id=trace_id,
        actor=user.email if user else "anonymous",
        action="auth_logout",
        resource_type="user",
        resource_id=user.id if user else "-",
        result="success" if revoked else "noop",
        request_summary="logout_with_revocation" if revoked else "logout_without_active_token",
    )
    return None


@router.post("/register", response_model=LoginResponse, status_code=status.HTTP_201_CREATED)
def register(payload: RegisterRequest, db: Session = Depends(get_db), trace_id: str = Depends(get_trace_id)) -> LoginResponse:
    existing = db.query(User).filter(User.email == payload.email).first()
    if existing:
        raise AppError(
            code="VALIDATION_ERROR",
            message="Email already registered",
            status_code=status.HTTP_400_BAD_REQUEST,
            details={"field": "email"},
        )
    user = AuthService.register(db, payload.email, payload.password, payload.display_name)
    tokens = AuthService._create_tokens(user.id)
    return LoginResponse(
        access_token=tokens[0],
        refresh_token=tokens[1],
        user=UserResponse.model_validate(user),
        trace_id=trace_id,
    )


@router.get("/me", response_model=UserResponse)
def me(current_user: User = Depends(get_current_user)) -> UserResponse:
    return UserResponse.model_validate(current_user)
