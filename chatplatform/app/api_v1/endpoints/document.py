from fastapi import APIRouter, UploadFile, File, HTTPException, status, Depends
from sqlalchemy.orm import Session

from chatplatform.app.api_v1.endpoints.auth import get_current_active_user
from chatplatform.db.models.admin import AdminUser
from chatplatform.db.session import DBSession
from chatplatform.schemas.document import DocumentOut, DocumentsResponse
from chatplatform.services.document_service import DocumentService

router = APIRouter()


@router.get("/", response_model=DocumentsResponse)
def get_documents(db_session: Session = Depends(DBSession.get_db),
                  current_user: AdminUser = Depends(get_current_active_user)):
    return DocumentService(db=db_session).get_all_documents_response()


@router.get("/{document_id}", response_model=DocumentOut)
async def get_document_by_id(document_id: int, db_session: Session = Depends(DBSession.get_db),
                             current_user: AdminUser = Depends(get_current_active_user)):
    document_service = DocumentService(db=db_session)
    document = await document_service.get_document_by_id(document_id)
    if not document:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found")
    return document


@router.post("/upload/{course_id}", response_model=DocumentOut)
async def upload_document_endpoint(course_id: int, file: UploadFile = File(...),
                                   db_session: Session = Depends(DBSession.get_db),
                                   current_user: AdminUser = Depends(get_current_active_user)):
    document_service = DocumentService(db=db_session)
    return document_service.upload_document(course_id=course_id, file=file)


@router.delete("/{document_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_document_endpoint(document_id: int,
                             db_session: Session = Depends(DBSession.get_db),
                             current_user: AdminUser = Depends(get_current_active_user)):
    document_service = DocumentService(db=db_session)
    if not document_service.delete_document(document_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found")
    return {"detail": "Document deleted successfully"}
