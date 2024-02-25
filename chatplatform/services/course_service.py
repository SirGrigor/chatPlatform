import os

from sqlalchemy import func

from chatplatform.db.models.course import Course
from chatplatform.db.models.document import Document
from chatplatform.schemas.course import CourseCreate, CoursesGPTRequest, CourseGPTRequest


class CourseService:
    def __init__(self, db):
        self.db = db

    def create_course(self, course_in: CourseCreate, user_id: int) -> Course:
        course_data = course_in.dict()
        course_data['created_by'] = user_id
        course_data['created_at'] = func.now()
        course_data['updated_at'] = func.now()

        db_course = Course(**course_data)
        self.db.add(db_course)
        self.db.commit()
        self.db.refresh(db_course)
        return db_course

    def get_courses(self) -> list[Course]:
        return self.db.query(Course).all()

    async def get_courses_by_admin_id(self, admin_id: int) -> CoursesGPTRequest:
        db_courses = self.db.query(Course).filter(Course.created_by == admin_id).all()
        course_outs = [CourseGPTRequest(title=course.title) for course in db_courses]
        courses_gpt_request = CoursesGPTRequest(courses=course_outs)

        return courses_gpt_request

    def delete_course(self, course_id: int) -> bool:
        """
        Deletes a course by its ID, including related documents.
        """
        # First, delete related documents
        documents = self.db.query(Document).filter(Document.course_id == course_id).all()
        for document in documents:
            # Delete physical file
            if os.path.exists(document.filepath):
                os.remove(document.filepath)
            self.db.delete(document)

        db_course = self.db.query(Course).filter(Course.id == course_id).first()
        if db_course:
            self.db.delete(db_course)
            self.db.commit()
            return True
        return False

    async def get_course_id_by_name(self, course_name: str) -> int:
        course = self.db.query(Course).filter(Course.title == course_name).first()
        if course:
            return course.id
        return 0

    def get_course_by_id(self, course_id: int) -> Course:
        course = self.db.query(Course).filter(Course.id == course_id).first()
        try:
            if course:
                return course
        except Exception as e:
            print(e)
            return None
