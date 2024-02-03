from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from db.session import get_db
from schemas.auth import Token, Login
from services.jwt_manager import create_access_token, create_external_refresh_token
from services.user_service import authenticate_user

router = APIRouter()


@router.post("/token", response_model=Token)
def login_for_access_token(form_data: Login, db: Session = Depends(get_db)):
    user = authenticate_user(db, form_data.email, form_data.password)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect username or password")

    access_token = create_access_token(data={"sub": user.username})
    return {
        "access_token": access_token,
        "token_type": "bearer"
    }


@router.post("/external/token", response_model=Token)
def get_external_access_token(email: str, password: str, db: Session = Depends(get_db)):
    user = authenticate_user(db, email, password)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect email or password")
    external_token = create_external_refresh_token(db=db, admin_id=user.id)
    return {
        "access_token": external_token.token,
        "token_type": "bearer"
    }
