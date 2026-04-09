from sqlalchemy.orm import Session

from app.models.models import User


def ensure_seed_data(db: Session) -> None:
    existing = db.query(User).filter(User.email == "demo@example.com").first()
    if existing:
        return
    db.add(User.demo())
    db.commit()
