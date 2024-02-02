from datetime import datetime, timedelta

from jose import jwt, JWTError
from sqlalchemy.orm import Session

from core.config import settings
from core.exceptions import WebSocketAuthException
from db.models.refresh_token import RefreshToken


def verify_token(token: str):
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        return payload  # Return user information or token payload as needed
    except JWTError:
        raise WebSocketAuthException("Invalid or expired token")


def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt


def create_refresh_token(db: Session, user_id: int, expires_delta: timedelta = timedelta(days=7)) -> RefreshToken:
    expire = datetime.utcnow() + expires_delta
    token_data = {"sub": str(user_id), "exp": expire}
    token = jwt.encode(token_data, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    db_refresh_token = RefreshToken(user_id=user_id, token=token, expires_at=expire, created_at=datetime.utcnow(), user_type="admin")
    db.add(db_refresh_token)
    db.commit()
    db.refresh(db_refresh_token)
    return db_refresh_token


def verify_token(token: str):
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        return payload
    except JWTError:
        raise JWTError("Invalid or expired token")
