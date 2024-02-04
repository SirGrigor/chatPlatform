from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from uvicorn import logging

from db.session import get_db
from services.gpt_chat_service import GptChatService
from schemas.gpt_model import GptPresetResponseSchema, GptPresetCreate, ChatResponse, \
    ChatRequest, GptModelListResponse, GptModelName  # Import the response schema

router = APIRouter()
gpt_chat_service = GptChatService()


@router.post("/", response_model=GptPresetResponseSchema)
def create_preset(preset_data: GptPresetCreate, db: Session = Depends(get_db)):
    try:
        preset = gpt_chat_service.create_gpt_preset(db, preset_data.dict(exclude_unset=True))
        return preset
    except Exception as e:
        logging.error(f"Failed to create preset: {e}")
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/chat/", response_model=ChatResponse)
async def start_chat(chat_request: ChatRequest, db: Session = Depends(get_db)):
    await gpt_chat_service.ask_gpt(db, chat_request.preset_id,
                                   chat_request.initial_message)
    try:
        response_message = await gpt_chat_service.ask_gpt(db, chat_request.preset_id,
                                                          chat_request.initial_message)
        return ChatResponse(message=response_message)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/models/", response_model=GptModelListResponse)
def get_supported_models():
    models = [model for model in GptModelName]
    return GptModelListResponse(models=models)
