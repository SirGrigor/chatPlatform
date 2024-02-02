from sqlalchemy import Column, Integer, Boolean, TIMESTAMP, ForeignKey
from sqlalchemy.orm import relationship, backref

from db.base_class import Base


class ChatSession(Base):
    __tablename__ = "chat_sessions"

    id = Column(Integer, primary_key=True, index=True)
    is_active = Column(Boolean, default=True)
    started_at = Column(TIMESTAMP, nullable=False)
    ended_at = Column(TIMESTAMP)
    external_user_id = Column(Integer, ForeignKey('external_users.id'), nullable=False)

    # Link back to the ExternalUser
    external_user = relationship("ExternalUser", backref=backref("chat_sessions", cascade="all, delete-orphan"))
