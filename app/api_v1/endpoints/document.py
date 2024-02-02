from typing import List

from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, status
from sqlalchemy.orm import Session

from db.session import get_db
from schemas.document import DocumentOut
from services.document_service import upload_document, get_documents_for_course, delete_document

router = APIRouter()


@router.post("/upload/{course_id}", response_model=DocumentOut)
async def upload_document_endpoint(course_id: int, file: UploadFile = File(...), db: Session = Depends(get_db)):
    # Assume base_path is configured elsewhere or passed as an environment variable
    document = upload_document(db=db, course_id=course_id, file=file, base_path="/app/documents")
    return document


@router.get("/{course_id}", response_model=List[DocumentOut])
def list_documents_endpoint(course_id: int, db: Session = Depends(get_db)):
    documents = get_documents_for_course(db=db, course_id=course_id)
    return documents


@router.delete("/documents/{document_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_document_endpoint(document_id: int, db: Session = Depends(get_db)):
    if not delete_document(db, document_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found")
    return {"detail": "Document deleted successfully"}
