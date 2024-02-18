from typing import List

from fastapi import APIRouter, UploadFile, File, HTTPException, status, Depends
from sqlalchemy.orm import Session

from db.session import DBSession
from schemas.document import DocumentOut
from services.document_service import DocumentService

router = APIRouter()


@router.post("/upload/{course_id}", response_model=DocumentOut)
async def upload_document_endpoint(course_id: int, file: UploadFile = File(...), db_session: Session = Depends(DBSession.get_db)):
    # Assume base_path is configured elsewhere or passed as an environment variable
    document_service = DocumentService(db=db_session)
    document = document_service.upload_document(course_id=course_id, file=file, base_path="/app/documents")
    return document


@router.get("/{course_id}", response_model=List[DocumentOut])
def list_documents_endpoint(course_id: int, db_session: Session = Depends(DBSession.get_db)):
    document_service = DocumentService(db=db_session)
    documents = document_service.get_documents_for_course(course_id=course_id)
    return documents


@router.delete("/documents/{document_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_document_endpoint(document_id: int, db_session: Session = Depends(DBSession.get_db)):
    document_service = DocumentService(db=db_session)
    if not document_service.delete_document(document_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found")
    return {"detail": "Document deleted successfully"}
