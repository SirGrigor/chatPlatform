from fastapi import APIRouter
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from fastapi.security import OAuth2PasswordRequestForm
from jose import JWTError
from requests import Session
from starlette import status
from typing_extensions import Annotated

from db.models.admin import AdminUser
from db.models.refresh_token import RefreshToken
from db.session import DBSession
from schemas.auth import Token
from schemas.user import UserOut, UserCreate
from services.jwt_manager import JWTManager, create_access_token
from services.jwt_manager import decode_token
from services.user_service import UserService

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


async def get_current_user(token: str = Depends(oauth2_scheme),
                           db: Session = Depends(DBSession.get_db)) -> AdminUser:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = await decode_token(token)  # Ensure decode_token is an async function
        print(f"Payload: {payload}")  # For debugging
        token_id = int(payload.get("sub"))  # Ensure the token actually contains 'admin_id'
        if token_id is None:
            raise credentials_exception
        user_id = db.query(RefreshToken).filter(RefreshToken.id == token_id).first().user_id
        user = db.query(AdminUser).filter(AdminUser.id == user_id).first()
        if user is None:
            raise credentials_exception
    except JWTError as e:
        print(f"JWTError: {e}")  # For debugging
        raise credentials_exception
    except Exception as e:
        print(f"Other Error: {e}")  # For debugging
        raise credentials_exception
    return user


async def get_current_active_user(
        current_user: Annotated[AdminUser, Depends(get_current_user)]
):
    if current_user.id is None:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user


@router.post("/register", response_model=UserOut)
def register_user(user_in: UserCreate, db: Session = Depends(DBSession.get_db)) -> UserOut:
    user_service = UserService(db=db)
    db_user = user_service.create_user(user_in=user_in)
    return db_user


@router.post("/login", response_model=Token)
def login(form_data: Annotated[OAuth2PasswordRequestForm, Depends()], db: Session = Depends(DBSession.get_db)):
    user_service = UserService(db=db)
    user = user_service.authenticate_user(email=form_data.username, password=form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = create_access_token(data={"sub": str(user.id)})
    return {"access_token": access_token, "token_type": "bearer"}


@router.post("/external/token", response_model=Token)
def get_external_access_token(db: Session = Depends(DBSession.get_db),
                              current_user: AdminUser = Depends(get_current_active_user)):
    jwt_manager = JWTManager(db=db)
    if not current_user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect jwt")
    external_token = jwt_manager.create_external_refresh_token(admin_id=current_user.id)
    external_token_string = external_token.token
    return {
        "access_token": external_token_string,
        "token_type": "websocket"
    }
