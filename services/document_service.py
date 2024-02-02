import shutil
import uuid

from fastapi import UploadFile
from sqlalchemy.orm import Session
from db.models import document as Document
import os


def save_document_file(file, file_path: str):
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)


def create_document(db: Session, course_id: int, filename: str, filepath: str, file_type: str) -> Document:
    db_document = Document(course_id=course_id, filename=filename, filepath=filepath, file_type=file_type)
    db.add(db_document)
    db.commit()
    db.refresh(db_document)
    return db_document


def get_documents_for_course(db: Session, course_id: int):
    return db.query(Document).filter(Document.course_id == course_id).all()


def upload_document(db: Session, course_id: int, file: UploadFile,
                    base_path: str = os.getenv("DOCUMENT_STORAGE_PATH", "/app/documents")):
    filename = file.filename
    file_extension = filename.split(".")[-1]
    file_path = os.path.join(base_path, f"{uuid.uuid4()}.{file_extension}")
    save_document_file(file, file_path)

    return create_document(db=db, course_id=course_id, filename=filename, filepath=file_path,
                           file_type=file.content_type)
