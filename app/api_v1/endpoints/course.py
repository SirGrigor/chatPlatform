from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from db.session import get_db
from schemas.course import CourseCreate, CourseOut
from services.course_service import create_course, get_courses

router = APIRouter()


@router.post("/", response_model=CourseOut)
def create_course_endpoint(course_in: CourseCreate, db: Session = Depends(get_db)):
    course = create_course(db=db, course_in=course_in)
    return course


@router.get("/", response_model=List[CourseOut])
def list_courses(db: Session = Depends(get_db)):
    courses = get_courses(db=db)
    return courses
