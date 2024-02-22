from datetime import datetime
from typing import List

from pydantic import BaseModel


class CourseCreate(BaseModel):
    title: str
    description: str


class CourseOut(BaseModel):
    id: int
    title: str
    description: str
    created_at: datetime


class CoursesListOut(BaseModel):
    courses: List[CourseOut]
    total: int

    class Config:
        orm_mode = True
