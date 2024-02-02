import shutil
import uuid

from fastapi import UploadFile
from sqlalchemy import func
from sqlalchemy.orm import Session
import os

from db.models.document import Document


def save_document_file(file, file_path: str):
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)


def create_document(db: Session, course_id: int, filename: str, filepath: str, file_type: str) -> Document:
    db_document = Document(course_id=course_id, filename=filename, filepath=filepath, file_type=file_type,
                           created_at=func.now(), updated_at=func.now())
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


def delete_document(db: Session, document_id: int) -> bool:
    """
    Deletes a document by its ID.

    :param db: SQLAlchemy Session object.
    :param document_id: ID of the document to delete.
    :return: True if the document was deleted, False otherwise.
    """
    db_document = db.query(Document).filter(Document.id == document_id).first()
    if db_document:
        # Delete physical file
        if os.path.exists(db_document.filepath):
            os.remove(db_document.filepath)
        db.delete(db_document)
        db.commit()
        return True
    return False
