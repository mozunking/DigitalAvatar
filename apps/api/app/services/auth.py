from sqlalchemy.orm import Session

from app.core.security import create_access_token, create_refresh_token, hash_password, verify_password
from app.models.models import User


class AuthService:
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
    def refresh(user: User) -> tuple[str, str]:
        return create_access_token(user.id), create_refresh_token(user.id)

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
