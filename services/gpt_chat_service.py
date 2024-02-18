import logging
from datetime import datetime, timedelta

import httpx
from openai import OpenAI
from sqlalchemy.orm import Session

from core.config import settings
from db.models.chat_session import ChatSession
from db.models.document import Document
from db.models.gpt_preset import GptPreset
from schemas.gpt_model import GptModelName
from schemas.nlp import QueryRequest
from services.nlp_service import LlamaService


class GptChatService:
    def __init__(self):
        self.client = OpenAI(api_key=settings.OPENAPI_KEY)
        self.nlp = LlamaService("/app/documents")

    @staticmethod
    def create_gpt_preset(db: Session, preset_data: dict) -> GptPreset:
        # Convert the Enum to its value (str) before saving
        if 'model' in preset_data and isinstance(preset_data['model'], GptModelName):
            preset_data['model'] = preset_data['model'].value
        db_preset = GptPreset(**preset_data)
        db.add(db_preset)
        db.commit()
        db.refresh(db_preset)
        return db_preset

    def is_chat_model(self, model_name: str) -> bool:
        """
        Check if the model is a chat model based on naming conventions.
        """
        # Adjust the logic as needed based on model naming conventions
        chat_models = {model.value for model in GptModelName}
        return model_name in chat_models

    async def ask_gpt(self, db: Session, initial_message: str, user_id: int):
        response = await self.nlp.search_in_documents(initial_message)
        yield response
