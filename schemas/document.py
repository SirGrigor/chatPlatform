from pydantic import BaseModel
from datetime import datetime


class DocumentBase(BaseModel):
    filename: str
    filepath: str
    file_type: str


class DocumentCreate(DocumentBase):
    pass


class DocumentOut(DocumentBase):
    id: int
    course_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True
