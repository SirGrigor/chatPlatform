from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from db.session import get_db
from schemas.user import UserCreate, UserOut
from services.user_service import create_user

router = APIRouter()


@router.post("/register", response_model=UserOut)
def register_user(user_in: UserCreate, db: Session = Depends(get_db)) -> UserOut:
    db_user = create_user(db=db, user_in=user_in)
    return db_user
