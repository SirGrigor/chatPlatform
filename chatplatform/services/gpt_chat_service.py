from llama_index.agent.openai import OpenAIAssistantAgent
from openai import OpenAI

from chatplatform.core.config import settings, logger
from chatplatform.db.models.gpt_preset import GptPreset
from chatplatform.db.session import DBSession
from chatplatform.schemas.course import CoursesGPTRequest
from chatplatform.schemas.gpt_model import GptModelName, PresetResponse, PresetSchemasResponse
from chatplatform.services.document_indexer_service import DocumentIndexer

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
        self.indexer = DocumentIndexer(db)
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
        response = await self.ask_gpt(initial_message, courses)
        yield response

    async def ask_gpt(self, initial_message: str, courses_request: CoursesGPTRequest) -> str:
        """
        Uses OpenAI's GPT to answer a question based on the indexed documents of specified courses.
        """
        query_engine_tools = []
        for course in courses_request.courses:
            course_name = course.title.replace(" ", "_")
            tool = await self.indexer.ensure_tool_for_course(course_name)
            if tool:
                query_engine_tools.append(tool)

        if not query_engine_tools:
            logger.error("No query engines loaded for the requested courses.")
            return "Error: Unable to process the request due to missing course data."

        agent = OpenAIAssistantAgent.from_new(
            name="Document Context GPT",
            instructions="You are an assistant with access to course documents. Use these documents to inform your answers.",
            tools=query_engine_tools,
            openai_tools=[],
            files=[],
            instructions_prefix="Please provide detailed, accurate, and informative answers."
        )
        response = agent.chat(initial_message)
        return response.response

    def get_presets(self, user_id: int) -> PresetSchemasResponse:
        # Fetch presets filtered by the given user_id, which seems to be intended as a course_id.
        presets = self.db.query(GptPreset).all()

        # Map each GptPreset instance to a PresetResponse object.
        # preset_schema_list = [PresetResponse(
        #     id=preset.id,
        #     name=preset.name,
        #     model=preset.model,
        #     max_tokens=preset.max_tokens,
        #     temperature=preset.temperature,
        #     course_id=preset.course_id  # Assuming this is intended as a course_id based on your initial method.
        # ) for preset in presets]

        # return PresetSchemasResponse(presets=preset_schema_list, total=len(presets))
        return presets
