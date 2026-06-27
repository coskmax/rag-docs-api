import bcrypt
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models import User


def _hash(password: str) -> str:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()


def create_user(db: Session, username: str, password: str) -> User:
    user = User(username=username, hashed_password=_hash(password))
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def get_user(db: Session, username: str) -> User | None:
    return db.execute(select(User).where(User.username == username)).scalar_one_or_none()


def verify_password(db: Session, username: str, password: str) -> bool:
    user = get_user(db, username)
    if not user:
        return False
    return bcrypt.checkpw(password.encode(), user.hashed_password.encode())
