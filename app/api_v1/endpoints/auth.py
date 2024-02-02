from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from db.session import get_db
from schemas.auth import Token, Login
from services.user_service import authenticate_user, create_user
from services.jwt_manager import create_access_token

router = APIRouter()


@router.post("/token", response_model=Token)
def login_for_access_token(form_data: Login, db: Session = Depends(get_db)):
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect username or password")
    access_token = create_access_token(data={"sub": user.username})
    return {"access_token": access_token, "token_type": "bearer"}

# Add registration and token refresh endpoints similarly
