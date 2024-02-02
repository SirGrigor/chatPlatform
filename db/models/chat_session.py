from sqlalchemy import Column, Integer, String, Boolean, TIMESTAMP, ForeignKey
from sqlalchemy.orm import relationship

from db.base_class import Base


class ChatSession(Base):
    __tablename__ = "chat_sessions"

    id = Column(Integer, primary_key=True, index=True)
    external_user_id = Column(Integer, ForeignKey('users.id'), nullable=True)
    course_token = Column(String(255), nullable=False)
    is_active = Column(Boolean, nullable=False, default=True)
    started_at = Column(TIMESTAMP, nullable=False)
    ended_at = Column(TIMESTAMP, nullable=True)

    course = relationship("Course", back_populates="chat_sessions")
    messages = relationship("Message", back_populates="chat_session")
