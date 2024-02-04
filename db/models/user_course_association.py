from sqlalchemy import Column, Integer, ForeignKey
from sqlalchemy.orm import relationship

from db.base_class import Base


class UserCourseAssociation(Base):
    __tablename__ = "user_course_association"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=True)
    course_id = Column(Integer, ForeignKey('courses.id'), nullable=False)
    course = relationship("Course", backref="user_course_association")
