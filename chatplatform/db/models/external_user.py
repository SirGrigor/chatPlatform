from sqlalchemy import Column, Integer, String, TIMESTAMP

from chatplatform.db.base_class import Base


class ExternalUser(Base):
    __tablename__ = "external_users"

    id = Column(Integer, primary_key=True, index=True)
    admin_id = Column(Integer, nullable=True)
    username = Column(String(255), nullable=False)
    created_at = Column(TIMESTAMP, nullable=False)
    updated_at = Column(TIMESTAMP)
    user_type = Column(String(255), nullable=False, default="external")
