from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


class CourseCreate(BaseModel):
    title: str
    description: str
    admin_user_id: int


class CourseOut(BaseModel):
    id: int
    title: str
    description: str
    admin_user_id: int
    created_at: datetime


class CoursesListOut(BaseModel):
    courses: List[CourseOut]
    total: int

    class Config:
        orm_mode = True
