from sqlalchemy import Column, Integer, String, Float, ForeignKey
from sqlalchemy.orm import relationship

from chatplatform.db.base_class import Base


class GptPreset(Base):
    __tablename__ = "gpt_presets"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False)
    model = Column(String, nullable=False)
    max_tokens = Column(Integer, default=150)
    temperature = Column(Float, default=0.7)
    course_id = Column(Integer, ForeignKey('courses.id'), nullable=False)
    course = relationship("Course", backref="gpt_presets")
