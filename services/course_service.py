from sqlalchemy.orm import Session
from db.models import course as Course
from schemas.course import CourseCreate


def create_course(db: Session, course_in: CourseCreate, user_id: int) -> Course:
    db_course = Course(**course_in.dict(), created_by=user_id)
    db.add(db_course)
    db.commit()
    db.refresh(db_course)
    return db_course


def get_courses(db: Session) -> list[Course]:
    return db.query(Course).all()
