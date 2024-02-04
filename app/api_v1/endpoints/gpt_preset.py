from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from uvicorn import logging

from db.session import get_db
from gptchat.gpt_chat_service import GptChatService
from schemas.gpt_model import GptPresetResponseSchema, GptPresetCreate  # Import the response schema

router = APIRouter()

@router.post("/", response_model=GptPresetResponseSchema)
def create_preset(preset_data: GptPresetCreate, db: Session = Depends(get_db)):
    try:
        preset = GptChatService.create_gpt_preset(db, preset_data.dict(exclude_unset=True))
        return preset
    except Exception as e:
        logging.error(f"Failed to create preset: {e}")
        raise HTTPException(status_code=400, detail=str(e))

