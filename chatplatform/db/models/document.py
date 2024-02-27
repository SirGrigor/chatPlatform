from sqlalchemy import Column, Integer, String, Text, TIMESTAMP, ForeignKey
from sqlalchemy.orm import relationship

from chatplatform.db.base_class import Base


class Document(Base):
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, index=True)
    course_id = Column(Integer, ForeignKey('courses.id'), nullable=False)
    filename = Column(String(255), nullable=False)
    filepath = Column(Text, nullable=False)
    file_type = Column(String(255), nullable=False)
    created_at = Column(TIMESTAMP, nullable=False)
    updated_at = Column(TIMESTAMP, nullable=False)
    document_content = Column(Text, nullable=True)  # Changed from String to Text
    document_metadata = Column(Text, nullable=True)  # Changed from String to Text
    doc_id = Column(String(255), nullable=True)
    course = relationship("Course", backref="documents")
