from sqlalchemy import Column, Integer, Boolean, TIMESTAMP, ForeignKey

from db.base_class import Base


class ChatSession(Base):
    __tablename__ = "chat_sessions"

    id = Column(Integer, primary_key=True, index=True)
    is_active = Column(Boolean, nullable=False, default=True)
    started_at = Column(TIMESTAMP, nullable=False)
    ended_at = Column(TIMESTAMP, nullable=True)
    external_user_id = Column(Integer, ForeignKey('external_users.id'), nullable=False)
