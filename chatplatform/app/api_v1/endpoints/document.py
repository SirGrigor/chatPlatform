from fastapi import APIRouter, UploadFile, File, HTTPException, status, Depends
from sqlalchemy.orm import Session

from chatplatform.db.session import DBSession
from chatplatform.schemas.document import DocumentOut, DocumentsResponse
from chatplatform.services.document_service import DocumentService
from chatplatform.services.nlp_service import LlamaService

router = APIRouter()


@router.get("/", response_model=DocumentsResponse)
def get_documents(db_session: Session = Depends(DBSession.get_db)):
    return DocumentService(db=db_session).get_all_documents_response()


@router.post("/upload/{course_id}", response_model=DocumentOut)
async def upload_document_endpoint(course_id: int, file: UploadFile = File(...),
                                   db_session: Session = Depends(DBSession.get_db)):
    return DocumentService(db=db_session).upload_document(course_id=course_id, file=file)


@router.post("/index")
async def index_document_endpoint(db_session: Session = Depends(DBSession.get_db)):
    llma_service = LlamaService(db_session)
    return await llma_service.index_document()


@router.delete("/{document_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_document_endpoint(document_id: int, db_session: Session = Depends(DBSession.get_db)):
    document_service = DocumentService(db=db_session)
    if not document_service.delete_document(document_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found")
    return {"detail": "Document deleted successfully"}
