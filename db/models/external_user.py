from sqlalchemy import Column, Integer, String, TIMESTAMP, ForeignKey
from sqlalchemy.orm import relationship

from db.base_class import Base


class ExternalUser(Base):
    __tablename__ = "external_users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(255), nullable=False)
    course_id = Column(Integer, ForeignKey('courses.id'), nullable=False)
    created_at = Column(TIMESTAMP, nullable=False)
    updated_at = Column(TIMESTAMP, nullable=True)

    course = relationship("Course", backref="external_users")
    chat_sessions = relationship("ChatSession", backref="external_user")
