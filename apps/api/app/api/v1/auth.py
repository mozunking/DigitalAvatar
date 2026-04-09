from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.core.deps import get_current_user, get_db, get_trace_id
from app.core.errors import AppError
from app.core.security import decode_token
from app.models.models import User
from app.schemas.common import LoginRequest, LoginResponse, LogoutRequest, RefreshRequest, RegisterRequest, UserResponse
from app.services.auth import AuthService

router = APIRouter()


@router.post("/login", response_model=LoginResponse)
def login(payload: LoginRequest, db: Session = Depends(get_db), trace_id: str = Depends(get_trace_id)) -> LoginResponse:
    tokens = AuthService.login(db, payload.email, payload.password)
    if not tokens:
        raise AppError(code="UNAUTHORIZED", message="Invalid email or password", status_code=status.HTTP_401_UNAUTHORIZED)
    access_token, refresh_token, user = tokens
    return LoginResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        user=UserResponse.model_validate(user),
        trace_id=trace_id,
    )


@router.post("/refresh", response_model=LoginResponse)
def refresh(payload: RefreshRequest, db: Session = Depends(get_db), trace_id: str = Depends(get_trace_id)) -> LoginResponse:
    try:
        claims = decode_token(payload.refresh_token)
    except ValueError as exc:
        raise AppError(code="UNAUTHORIZED", message="Invalid refresh token", status_code=status.HTTP_401_UNAUTHORIZED) from exc
    if claims.get("type") != "refresh":
        raise AppError(code="UNAUTHORIZED", message="Invalid refresh token", status_code=status.HTTP_401_UNAUTHORIZED)
    user = db.get(User, claims.get("sub"))
    if not user:
        raise AppError(code="UNAUTHORIZED", message="User not found", status_code=status.HTTP_401_UNAUTHORIZED)
    access_token, refresh_token = AuthService.refresh(user)
    return LoginResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        user=UserResponse.model_validate(user),
        trace_id=trace_id,
    )


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
def logout(payload: LogoutRequest) -> None:
    return None


@router.post("/register", response_model=LoginResponse, status_code=status.HTTP_201_CREATED)
def register(payload: RegisterRequest, db: Session = Depends(get_db), trace_id: str = Depends(get_trace_id)) -> LoginResponse:
    existing = db.query(User).filter(User.email == payload.email).first()
    if existing:
        raise AppError(code="CONFLICT", message="Email already registered", status_code=status.HTTP_409_CONFLICT)
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
