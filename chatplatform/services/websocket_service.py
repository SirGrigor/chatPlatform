import datetime
from typing import AsyncGenerator, List

from chatplatform.db.models.course import Course
from chatplatform.db.models.external_user import ExternalUser
from chatplatform.schemas.course import CoursesGPTRequest
from chatplatform.services.gpt_chat_service import GptChatService
from chatplatform.services.jwt_manager import verify_external_token


class WebSocketService:
    def __init__(self, db_session):
        self.db = db_session

    async def get_or_create_external_user(self, username: str, admin_id=int) -> ExternalUser:
        user = self.db.query(ExternalUser).filter_by(username=username).first()
        if not user:
            user = ExternalUser(username=username, admin_id=admin_id, created_at=datetime.datetime.now(), user_type="external")
            self.db.add(user)
            self.db.commit()
        return user

    async def generate_gpt_responses(self, message: str, courses: CoursesGPTRequest) -> AsyncGenerator[str, None]:
        gpt_chat_service = GptChatService(self.db)
        async for response_chunk in gpt_chat_service.request_nlp(message, courses):
            yield response_chunk

    async def verify_external_token(self, token: str) -> tuple[int, str]:
        return await verify_external_token(token)
