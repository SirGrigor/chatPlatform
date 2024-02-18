from fastapi import APIRouter

from schemas.nlp import QueryRequest
from services.nlp_service import LlamaService

router = APIRouter()
llama_service = LlamaService(document_path="data")


@router.post("/search/", response_model=str)
async def search_documents(request: QueryRequest):
    return llama_service.search_in_documents(request.user_request)
