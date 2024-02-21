import datetime

from fastapi import HTTPException

from db.models.admin import AdminUser
from core.security import get_password_hash, verify_password
from db.models.refresh_token import RefreshToken
from schemas.user import UserCreate
from typing import Optional

from services.jwt_manager import JWTManager


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

    def authenticate_user(self, email: str, password: str) -> RefreshToken:
        user = self.db.query(AdminUser).filter(AdminUser.email == email).first()
        if not user:
            HTTPException(status_code=401, detail="User not found")
        if not verify_password(password, user.password_hash):
            HTTPException(status_code=401, detail="Incorrect username or password")
        return self.jwt_manager.create_refresh_token(user_id=user.id)

    def authenticate_user_by_jwt(self, jwt: str) -> Optional[AdminUser]:
        user_id, user_type = self.jwt_manager.verify_token(jwt)
        if not user_id or user_type != "admin":
            return None
        user = self.db.query(AdminUser).filter(AdminUser.id == user_id).first()
        return user
