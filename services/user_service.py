import datetime

from db.models.admin import AdminUser
from core.security import get_password_hash, verify_password
from schemas.user import UserCreate
from typing import Optional

from services.jwt_manager import verify_token, JWTManager


def authenticate_user_by_jwt(jwt: str) -> Optional[AdminUser]:
    user = verify_token(jwt)
    if not user:
        return None
    return user


class UserService:
    def __init__(self, db):
        self.db = db
        self.jwt_manager = JWTManager(db=db)

    def create_user(self, user_in: UserCreate) -> AdminUser:
        hashed_password = get_password_hash(user_in.password)
        db_user = AdminUser(email=user_in.email, username=user_in.username, password_hash=hashed_password,
                            created_at=datetime.datetime.now())
        self.db.add(db_user)
        self.db.commit()
        self.db.refresh(db_user)

        self.jwt_manager.create_refresh_token(user_id=db_user.id)
        return db_user

    def authenticate_user(self, email: str, password: str) -> Optional[AdminUser]:
        user = self.db.query(AdminUser).filter(AdminUser.email == email).first()
        if not user:
            return None
        if not verify_password(password, user.password_hash):
            return None
        return user
