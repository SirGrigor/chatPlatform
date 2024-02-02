from sqlalchemy import Column, Integer, String, Text, TIMESTAMP, ForeignKey

from db.base_class import Base


class Course(Base):
    __tablename__ = "courses"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    widget_token = Column(String(255), unique=True, nullable=False)
    created_by = Column(Integer, ForeignKey('admin_users.id'), nullable=False)
    created_at = Column(TIMESTAMP, nullable=False)
    updated_at = Column(TIMESTAMP, nullable=False)
