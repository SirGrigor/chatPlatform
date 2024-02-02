from sqlalchemy import Column, Integer, String, TIMESTAMP, ForeignKey
from sqlalchemy.orm import relationship

from db.base_class import Base
from db.models.user_course_association import user_course_association


class ExternalUser(Base):
    __tablename__ = "external_users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(255), nullable=False)
    created_at = Column(TIMESTAMP, nullable=False)
    updated_at = Column(TIMESTAMP)

    # Many-to-many relationship with Course
    courses = relationship("Course", secondary=user_course_association, back_populates="external_users")
