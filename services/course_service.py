import os

from sqlalchemy import func
from sqlalchemy.orm import Session

from db.models.course import Course
from db.models.document import Document
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


def delete_course(db: Session, course_id: int) -> bool:
    """
    Deletes a course by its ID, including related documents.
    """
    # First, delete related documents
    documents = db.query(Document).filter(Document.course_id == course_id).all()
    for document in documents:
        # Delete physical file
        if os.path.exists(document.filepath):
            os.remove(document.filepath)
        db.delete(document)

    # Then, delete the course
    db_course = db.query(Course).filter(Course.id == course_id).first()
    if db_course:
        db.delete(db_course)
        db.commit()
        return True
    return False

async def get_course_id_by_name(db: Session, course_name: str) -> int:
    course = db.query(Course).filter(Course.title == course_name).first()
    if course:
        return course.id
    return 0