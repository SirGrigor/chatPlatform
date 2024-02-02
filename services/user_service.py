from sqlalchemy.orm import Session
from db.models.user import User
from core.security import get_password_hash, verify_password
from schemas.user import UserCreate
from typing import Optional

from services.jwt_manager import create_refresh_token


def create_user(db: Session, user_in: UserCreate) -> User:
    hashed_password = get_password_hash(user_in.password)
    db_user = User(email=user_in.email, username=user_in.username, password_hash=hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)

    # Create a refresh token for the new user using the JWT manager
    create_refresh_token(db=db, user_id=db_user.id)

    return db_user


def authenticate_user(db: Session, email: str, password: str) -> Optional[User]:
    user = db.query(User).filter(User.email == email).first()
    if not user:
        return None
    if not verify_password(password, user.password_hash):
        return None
    return user
