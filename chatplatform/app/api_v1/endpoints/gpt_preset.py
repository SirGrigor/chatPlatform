from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from starlette.requests import Request
from starlette.responses import HTMLResponse
from starlette.templating import Jinja2Templates
from uvicorn import logging

from chatplatform.db.session import DBSession
from chatplatform.schemas.gpt_model import GptPresetResponseSchema, GptPresetCreate, GptModelDetailsResponse, get_model_details
from chatplatform.services.gpt_chat_service import GptChatService

router = APIRouter()
templates = Jinja2Templates(directory="chatplatform/app/api_v1/templates/")


@router.post("/", response_model=GptPresetResponseSchema)
def create_preset(preset_data: GptPresetCreate, db_session: Session = Depends(DBSession.get_db)):
    gpt_chat_service = GptChatService(db=db_session)
    try:
        preset = gpt_chat_service.create_gpt_preset(preset_data.dict(exclude_unset=True))
        return preset
    except Exception as e:
        logging.error(f"Failed to create preset: {e}")
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/models/", response_model=GptModelDetailsResponse)
def get_supported_models():
    models = get_model_details()
    return GptModelDetailsResponse(models=models)


@router.get("/chat/window/", response_class=HTMLResponse)
async def chat_window(request: Request):
    return templates.TemplateResponse("chat.html", {"request": request})
