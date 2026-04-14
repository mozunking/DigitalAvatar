from datetime import datetime
from typing import NamedTuple

from sqlalchemy.orm import Session

from app.core.security import create_access_token, create_refresh_token, decode_token, hash_password, token_expiry, verify_password
from app.models.models import RevokedToken, User


class RevocationResult(NamedTuple):
    user: User | None
    revoked: bool


class AuthService:
    @staticmethod
    def is_token_revoked(db: Session, jti: str | None) -> bool:
        if not jti:
            return True
        return db.query(RevokedToken).filter(RevokedToken.token_jti == jti).first() is not None

    @staticmethod
    def revoke_token_claims(db: Session, claims: dict, *, token_type: str | None = None) -> RevocationResult:
        resolved_token_type = str(claims.get("type", "")).strip().lower()
        if token_type and resolved_token_type != token_type:
            return RevocationResult(user=None, revoked=False)
        token_jti = claims.get("jti")
        user_id = claims.get("sub")
        user = db.get(User, user_id) if user_id else None
        if not user or AuthService.is_token_revoked(db, token_jti):
            return RevocationResult(user=user, revoked=False)
        revoked = RevokedToken(
            user_id=user.id,
            token_jti=token_jti,
            token_type=resolved_token_type,
            expires_at=token_expiry(claims),
        )
        db.add(revoked)
        db.commit()
        return RevocationResult(user=user, revoked=True)

    @staticmethod
    def revoke_token(db: Session, token: str, *, token_type: str | None = None) -> RevocationResult:
        try:
            claims = decode_token(token)
        except ValueError:
            return RevocationResult(user=None, revoked=False)
        return AuthService.revoke_token_claims(db, claims, token_type=token_type)

    @staticmethod
    def login(db: Session, email: str, password: str) -> tuple[str, str, User] | None:
        user = db.query(User).filter(User.email == email).first()
        if not user or not verify_password(password, user.hashed_password):
            if user:
                user.failed_login_count += 1
                db.add(user)
                db.commit()
            return None
        user.failed_login_count = 0
        db.add(user)
        db.commit()
        return create_access_token(user.id), create_refresh_token(user.id), user

    @staticmethod
    def refresh(db: Session, refresh_token: str) -> tuple[str, str, User] | None:
        try:
            claims = decode_token(refresh_token)
        except ValueError:
            return None
        revocation = AuthService.revoke_token_claims(db, claims, token_type="refresh")
        if not revocation.revoked or not revocation.user:
            return None
        return create_access_token(revocation.user.id), create_refresh_token(revocation.user.id), revocation.user

    @staticmethod
    def _create_tokens(user_id: str) -> tuple[str, str]:
        return create_access_token(user_id), create_refresh_token(user_id)

    @staticmethod
    def register(db: Session, email: str, password: str, display_name: str | None) -> User:
        user = User(email=email, hashed_password=hash_password(password), display_name=display_name or email.split("@")[0])
        db.add(user)
        db.commit()
        db.refresh(user)
        return user
