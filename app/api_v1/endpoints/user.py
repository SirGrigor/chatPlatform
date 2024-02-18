from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from db.session import DBSession
from schemas.user import UserCreate, UserOut
from services.user_service import UserService

router = APIRouter()


@router.post("/register", response_model=UserOut)
def register_user(user_in: UserCreate, db: Session = Depends(DBSession.get_db)) -> UserOut:
    user_service = UserService(db=db)
    db_user = user_service.create_user(user_in=user_in)
    return db_user
