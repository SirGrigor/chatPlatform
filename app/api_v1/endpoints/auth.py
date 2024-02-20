from fastapi import APIRouter, HTTPException, status, Depends
from sqlalchemy.orm import Session

from db.session import DBSession
from schemas.auth import Token, Login
from services.jwt_manager import create_access_token, JWTManager
from services.user_service import UserService

router = APIRouter()


@router.post("/token", response_model=Token)
def login_for_access_token(form_data: Login, db: Session = Depends(DBSession.get_db)):
    user_service = UserService(db=db)
    user = user_service.authenticate_user(form_data.email, form_data.password)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect username or password")

    access_token = create_access_token(data={"sub": user.username})
    return {
        "access_token": access_token,
        "token_type": "bearer"
    }


@router.post("/external/token", response_model=Token)
def get_external_access_token(jwt: str, db: Session = Depends(DBSession.get_db)):
    jwt_manager = JWTManager(db=db)
    user_service = UserService(db=db)
    user = user_service.authenticate_user_by_jwt(jwt)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect jwt")
    external_token = jwt_manager.create_external_refresh_token(admin_id=user.id)
    external_token_string = external_token.token
    return {
        "access_token": external_token_string,
        "token_type": "websocket"
    }
