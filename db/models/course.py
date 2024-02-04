from sqlalchemy import Column, Integer, String, Text, TIMESTAMP, ForeignKey, func

from db.base_class import Base


class Course(Base):
    __tablename__ = "courses"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    created_by = Column(Integer, ForeignKey('admin_users.id'), nullable=False)
    created_at = Column(TIMESTAMP, nullable=False, server_default=func.now())
    updated_at = Column(TIMESTAMP, nullable=False, server_default=func.now(), onupdate=func.now())


