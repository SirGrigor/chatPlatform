from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class CourseCreate(BaseModel):
    title: str
    description: str


class CourseOut(CourseCreate):
    id: int
    created_by: int
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        orm_mode = True
