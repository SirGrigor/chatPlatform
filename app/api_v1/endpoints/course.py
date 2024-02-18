from fastapi import APIRouter, HTTPException, status, Depends
from sqlalchemy.orm import Session

from db.models.course import Course
from db.session import DBSession
from schemas.course import CourseCreate, CourseOut, CoursesListOut
from services.course_service import CourseService

router = APIRouter()


@router.post("/", response_model=CourseOut)
def create_course_endpoint(course_in: CourseCreate, db_session: Session = Depends(DBSession.get_db)):
    course_service = CourseService(db=db_session)
    course = course_service.create_course(course_in=course_in, user_id=course_in.admin_user_id)
    course_out = CourseOut(id=course.id, title=course.title, description=course.description,
                           admin_user_id=course.created_by, created_at=course.created_at)
    return course_out


@router.get("/", response_model=CoursesListOut)
def read_courses(db_session: Session = Depends(DBSession.get_db)):
    courses_query = db_session.query(Course).all()
    courses_list = [CourseOut(id=course.id, title=course.title, description=course.description,
                              admin_user_id=course.created_by, created_at=course.created_at) for course in
                    courses_query]
    return CoursesListOut(courses=courses_list, total=len(courses_list))


@router.delete("/courses/{course_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_course_endpoint(course_id: int, db_session: Session = Depends(DBSession.get_db)):
    course_service = CourseService(db=db_session)
    if not course_service.delete_course(course_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Course not found")
    return {"detail": "Course deleted successfully"}
