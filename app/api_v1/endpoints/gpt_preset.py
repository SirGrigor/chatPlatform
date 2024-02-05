from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from uvicorn import logging

from db.session import get_db
from services.gpt_chat_service import GptChatService
from schemas.gpt_model import GptPresetResponseSchema, GptPresetCreate, ChatResponse, \
    ChatRequest, GptModelDetailsResponse, get_model_details

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
    try:
        response_message, response_id, user_id = await gpt_chat_service.ask_gpt(db, chat_request.preset_id,
                                                                       chat_request.initial_message, chat_request.user_id)
        return ChatResponse(message=response_message, response_id=response_id, user_id=user_id)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/models/", response_model=GptModelDetailsResponse)
def get_supported_models():
    models = get_model_details()
    return GptModelDetailsResponse(models=models)
