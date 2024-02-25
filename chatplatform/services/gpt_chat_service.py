from openai import OpenAI
from chatplatform.core.config import settings
from chatplatform.db.models.course import Course
from chatplatform.db.models.gpt_preset import GptPreset
from chatplatform.db.session import DBSession
from chatplatform.schemas.course import CoursesGPTRequest
from chatplatform.schemas.gpt_model import GptModelName
from chatplatform.services.nlp_service import LlamaService

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
        self.nlp = LlamaService(db)
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

    async def request_nlp(self, initial_message: str, courses: CoursesGPTRequest):
        response = await self.nlp.ask_gpt(initial_message, courses)
        yield response
