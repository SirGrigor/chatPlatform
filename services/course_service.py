from sqlalchemy import func
from sqlalchemy.orm import Session

from db.models.course import Course
from schemas.course import CourseCreate


def create_course(db: Session, course_in: CourseCreate, user_id: int) -> Course:
    # Convert course_in (Pydantic model) to dictionary and update created_by field
    course_data = course_in.dict()
    course_data['created_by'] = user_id  # Use 'created_by' to match the Course model
    course_data['created_at'] = func.now()
    course_data['updated_at'] = func.now()
    # Remove 'admin_user_id' from course_data if it exists
    course_data.pop('admin_user_id', None)

    # Create and add the course to the database
    db_course = Course(**course_data)
    db.add(db_course)
    db.commit()
    db.refresh(db_course)
    return db_course


def get_courses(db: Session) -> list[Course]:
    return db.query(Course).all()
