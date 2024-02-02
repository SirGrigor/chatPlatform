from sqlalchemy import Column, Integer, String, TIMESTAMP

from db.base_class import Base

class RefreshToken(Base):
    __tablename__ = "refresh_tokens"

    id = Column(Integer, primary_key=True, index=True)
    token = Column(String(255), unique=True, nullable=False)
    expires_at = Column(TIMESTAMP, nullable=False)
    created_at = Column(TIMESTAMP, nullable=False)
    user_id = Column(Integer, nullable=False)
    user_type = Column(String(50), nullable=False)
