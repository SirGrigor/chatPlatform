from sqlalchemy import Column, Integer, String, Text, ForeignKey, TIMESTAMP
from sqlalchemy.orm import relationship

from ..base_class import Base


class Document(Base):
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, index=True)
    course_id = Column(Integer, ForeignKey('courses.id'), nullable=False)
    filename = Column(String(255), nullable=False)
    filepath = Column(Text, nullable=False)
    file_type = Column(String(50), nullable=False)
    created_at = Column(TIMESTAMP, nullable=False)
    updated_at = Column(TIMESTAMP, nullable=False)

    course = relationship("Course", back_populates="documents")
