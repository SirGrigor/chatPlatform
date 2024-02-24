from datetime import datetime
from typing import List

from pydantic import BaseModel


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
    filename: str
    filepath: str
    file_type: str

    class Config:
        orm_mode = True


class DocumentsResponse(BaseModel):
    documents: List[DocumentOut]
    total: int
