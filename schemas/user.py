from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr


class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str


class UserOut(BaseModel):
    id: int
    username: str
    email: EmailStr
    user_type: str
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        orm_mode = True
