import os
import shutil
import uuid
from typing import List

from fastapi import UploadFile
from sqlalchemy import func

from chatplatform.core.config import logger
from chatplatform.db.models.document import Document
from chatplatform.schemas.document import DocumentOut, DocumentsResponse
from chatplatform.services.course_service import CourseService
from chatplatform.services.nlp_service import LlamaService


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

    def __init__(self, db):
        """
        Initializes the DocumentService with a base path for storing documents.

        :param base_path: Base directory path where documents will be saved.
        """
        self.db = db
        self.base_path = os.getenv("DOCUMENT_STORAGE_PATH", "/app/documents")

    async def create_document(self, course_id: int, filename: str, filepath: str, file_type: str) -> Document:
        llma_service = LlamaService(self.db)
        db_document = Document(course_id=course_id, filename=filename,
                               filepath=filepath, file_type=file_type,
                               created_at=func.now(), updated_at=func.now())
        self.db.add(db_document)
        self.db.commit()
        self.db.refresh(db_document)
        await llma_service.index_document()
        return db_document

    async def upload_document(self, file: UploadFile, course_id: int):
        """
         Handles the uploading and saving of a document under a directory named after the course,
        with the directory structure including the actual document name.

        :param course_id:
        :param file: UploadFile object from FastAPI.
        :return: Path where the file was saved.
        """

        course_service = CourseService(self.db)
        course = course_service.get_course_by_id(course_id)
        course_name = course.title.replace(" ", "_")
        logger.info(
            f"Uploading document for course: {course_name}, course_id: {course_id}, file: {file.filename}, file_type: {file.content_type}")

        file_extension = os.path.splitext(file.filename)[-1].lower()  # Ensure extension is in lowercase
        allowed_extensions = {".json", ".xml", ".pdf", ".docx"}
        logger.info(f"File extension: {file_extension}")
        if file_extension not in allowed_extensions:
            raise ValueError("Unsupported file type.")

        # Correct path construction
        file_path = os.path.join(self.base_path, course_name, f"{uuid.uuid4()}{file_extension}")
        os.makedirs(os.path.dirname(file_path), exist_ok=True)  # Ensure the course directory exists

        save_document_file(file, file_path)  # Assuming this function exists and correctly saves the file
        return await self.create_document(course_id=course_id,
                                    filename=file.filename,
                                    filepath=file_path,
                                    file_type=file.content_type)

    def get_documents_for_course(self, course_id: int):
        return self.db.query(Document).filter(Document.course_id == course_id).all()

    async def delete_document(self, document_id: int) -> bool:
        """
    Deletes a document by its ID.
    :param db: SQLAlchemy Session object.
    :param document_id: ID of the document to delete.
    :return: True if the document was deleted, False otherwise.
    """
        llma_service = LlamaService(self.db)
        db_document = self.db.query(Document).filter(Document.id == document_id).first()
        if db_document:
            if os.path.exists(db_document.filepath):
                os.remove(db_document.filepath)
                self.db.delete(db_document)
                self.db.commit()
                await llma_service.index_document()
                return True
        return False

    def get_all_documents_response(self) -> DocumentsResponse:
        documents = self.db.query(Document).all()
        document_out_list = [DocumentOut(
            id=document.id,
            course_id=document.course_id,
            created_at=document.created_at,
            updated_at=document.updated_at,
            filename=document.filename,
            filepath=document.filepath,
            file_type=document.file_type,
        ) for document in documents]
        return DocumentsResponse(documents=document_out_list, total=len(documents))

    async def get_documents(self) -> List[Document]:
        documents = self.db.query(Document).all()
        return documents

    async def get_document_by_id(self, document_id: int) -> DocumentOut:
        document = self.db.query(Document).filter(Document.id == document_id).first()
        return DocumentOut(
            id=document.id,
            course_id=document.course_id,
            created_at=document.created_at,
            updated_at=document.updated_at,
            filename=document.filename,
            filepath=document.filepath,
            file_type=document.file_type,
        )
