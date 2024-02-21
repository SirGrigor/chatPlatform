import os
import shutil
import uuid

from fastapi import UploadFile
from sqlalchemy import func

from db.models.document import Document


def save_document_file(file, file_path: str):
    """
    Saves the uploaded file to the specified path.

    :param file: UploadFile object from FastAPI.
    :param file_path: String, path where the file will be saved.
    """
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)


class DocumentService:
    """
    Service class for handling document file operations such as saving.
    """

    def __init__(self, db, base_path: str = os.getenv("DOCUMENT_STORAGE_PATH", "/app/documents")):
        """
        Initializes the DocumentService with a base path for storing documents.

        :param base_path: Base directory path where documents will be saved.
        """
        self.db = db
        self.base_path = base_path

    def create_document(self, course_id: int, filename: str, filepath: str, file_type: str) -> Document:
        db_document = Document(course_id=course_id, filename=filename,
                               filepath=filepath, file_type=file_type,
                               created_at=func.now(), updated_at=func.now())
        self.db.add(db_document)
        self.db.commit()
        self.db.refresh(db_document)
        return db_document

    def upload_document(self, file: UploadFile, course_id: int):
        """
        Handles the uploading and saving of a document.

        :param course_id:
        :param file: UploadFile object from FastAPI.
        :return: Path where the file was saved.
        """
        filename = file.filename
        file_extension = filename.split(".")[-1].lower()  # Ensure extension is in lowercase
        allowed_extensions = {"json", "xml", "pdf", "docx"}

        if file_extension not in allowed_extensions:
            raise ValueError("Unsupported file type.")

        file_path = os.path.join(self.base_path, f"{uuid.uuid4()}.{file_extension}")
        save_document_file(file, file_path)
        return self.create_document(course_id=course_id, filename=filename, filepath=file_path,
                                    file_type=file.content_type)

    def get_documents_for_course(self, course_id: int):
        return self.db.query(Document).filter(Document.course_id == course_id).all()

    def delete_document(self, document_id: int) -> bool:
        """
        Deletes a document by its ID.

        :param db: SQLAlchemy Session object.
        :param document_id: ID of the document to delete.
        :return: True if the document was deleted, False otherwise.
        """

        db_document = self.db.query(Document).filter(Document.id == document_id).first()
        if db_document:
            if os.path.exists(db_document.filepath):
                os.remove(db_document.filepath)
                self.db.delete(db_document)
                self.db.commit()
                return True
        return False
