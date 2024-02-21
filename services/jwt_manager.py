import logging

from fastapi.logger import logger
from datetime import datetime, timedelta

from fastapi import HTTPException
from jose import jwt, JWTError

from core.config import settings
from db.models.refresh_token import RefreshToken

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("chatplatform")


# Now you can use logger.info(), logger.debug(), etc.

def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta

    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
        return encoded_jwt


async def verify_external_token(token: str):
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        admin_id = payload.get("admin_id")
        user_type = payload.get("type")
        if user_type != "external_admin":
            raise HTTPException(status_code=401, detail="Invalid token type")
        return admin_id, user_type
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid or expired token")


class JWTManager:
    def __init__(self, db):
        self.db = db

    def create_refresh_token(self, user_id: int,
                             expires_delta: timedelta = timedelta(hours=1)) -> RefreshToken:
        expire = datetime.utcnow() + expires_delta
        token_data = {"sub": str(user_id), "exp": expire}
        token = jwt.encode(token_data, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
        return self.record_token(expire, token, user_id)

    def record_token(self, expire, token, user_id):
        db_refresh_token = RefreshToken(user_id=user_id, token=token, expires_at=expire,
                                        created_at=datetime.utcnow(),
                                        user_type="admin")
        self.db.add(db_refresh_token)
        self.db.commit()
        self.db.refresh(db_refresh_token)
        return db_refresh_token

    def create_external_refresh_token(self, admin_id: int,
                                      expires_delta: timedelta = timedelta(hours=1)) -> RefreshToken:
        expire = datetime.utcnow() + expires_delta
        token_data = {"admin_id": str(admin_id), "exp": expire, "type": "external_admin"}
        token = jwt.encode(token_data, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
        db_refresh_token = RefreshToken(user_id=admin_id, token=token, expires_at=expire, created_at=datetime.utcnow(),
                                        user_type="external_admin")
        self.db.add(db_refresh_token)
        self.db.commit()
        self.db.refresh(db_refresh_token)
        return db_refresh_token

    def verify_token(self, token: str):
        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
            user_id = payload.get("sub")
            if user_id is None:
                raise HTTPException(status_code=401, detail="Invalid token data. Missing user ID.")
            db_token = self.db.query(RefreshToken).filter(RefreshToken.token == token,
                                                          RefreshToken.user_id == user_id).first()
            if db_token is None or db_token.expires_at < datetime.utcnow():
                raise HTTPException(status_code=401, detail="Token not found or has expired.")

            return db_token.user_id, db_token.user_type
        except JWTError as e:
            raise HTTPException(status_code=401, detail=f"Invalid or expired token: {str(e)}")
