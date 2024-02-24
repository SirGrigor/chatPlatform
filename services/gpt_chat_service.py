import asyncio

from openai import OpenAI
from core.config import settings
from db.models.gpt_preset import GptPreset
from db.session import DBSession
from schemas.gpt_model import GptModelName
from services.nlp_service import LlamaService

db_session = DBSession().get_db()


def is_chat_model(model_name: str) -> bool:
    """
    Check if the model is a chat model based on naming conventions.
    """
    chat_models = {model.value for model in GptModelName}
    return model_name in chat_models


class GptChatService:
    def __init__(self, db):
        self.client = OpenAI(api_key=settings.OPENAPI_KEY)
        self.nlp = LlamaService("/app/documents")
        self.db = db

    def create_gpt_preset(self, preset_data: dict) -> GptPreset:
        # Convert the Enum to its value (str) before saving
        if 'model' in preset_data and isinstance(preset_data['model'], GptModelName):
            preset_data['model'] = preset_data['model'].value
        db_preset = GptPreset(**preset_data)
        self.db.add(db_preset)
        self.db.commit()
        self.db.refresh(db_preset)
        return db_preset

    async def ask_gpt(self, initial_message: str, user_id: int):
        response = await self.nlp.search_in_documents(initial_message)
        yield response
