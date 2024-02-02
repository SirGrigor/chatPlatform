from sqlalchemy import Column, Integer, Text, Boolean, TIMESTAMP, ForeignKey
from sqlalchemy.orm import relationship

from ..base_class import Base

class Message(Base):
    __tablename__ = "messages"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey('chat_sessions.id'), nullable=False)
    text = Column(Text, nullable=False)
    is_user_message = Column(Boolean, nullable=False)
    created_at = Column(TIMESTAMP, nullable=False)

    chat_session = relationship("ChatSession", back_populates="messages")
