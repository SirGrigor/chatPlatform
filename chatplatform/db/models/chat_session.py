import json
import logging
from datetime import datetime, timedelta

from sqlalchemy import Column, Integer, Boolean, String, TIMESTAMP, ForeignKey, Text
from sqlalchemy.orm import relationship, backref

from chatplatform.db.base_class import Base


class ChatSession(Base):
    __tablename__ = "chat_sessions"

    id = Column(Integer, primary_key=True, index=True)
    is_active = Column(Boolean, default=True)
    started_at = Column(TIMESTAMP, nullable=False)
    ended_at = Column(TIMESTAMP)
    external_user_id = Column(Integer, ForeignKey('external_users.id'), nullable=False)
    external_user = relationship("ExternalUser", backref=backref("chat_sessions", cascade="all, delete-orphan"))
    conversation_history = Column(Text, nullable=True)  # Changed from String to Text

    def set_conversation_history(self, history):
        self.conversation_history = json.dumps(history)

    def get_conversation_history(self):
        return json.loads(self.conversation_history) if self.conversation_history else []

    def is_active_based_on_time(self, lifetime_hours=24):
        """Check if the session is still active based on its start time and a defined lifetime."""
        now = datetime.now()
        return now - self.started_at < timedelta(hours=lifetime_hours)

    def clear_conversation_history(self):
        """Clears the conversation history."""
        logging.info(f"Clearing conversation history for session {self.id}")
        self.conversation_history = None
