import logging
from datetime import datetime, timedelta
from typing import Optional, Tuple

from fastapi import HTTPException
from openai import OpenAI
from sqlalchemy import select
from sqlalchemy.orm import Session

from core.config import settings
from db.models.chat_session import ChatSession
from db.models.gpt_preset import GptPreset
from schemas.gpt_model import GptModelName


class GptChatService:
    def __init__(self):
        self.client = OpenAI(api_key=settings.OPENAPI_KEY)

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

    @staticmethod
    def get_gpt_preset(db: Session, preset_id: int) -> GptPreset:
        """
        Retrieves a GPT preset by ID from the database.
        """
        return db.query(GptPreset).filter(GptPreset.id == preset_id).first()

    @staticmethod
    def _get_context_from_file(filepath: str) -> str:
        """
        Extracts context from a given file.
        """
        try:
            with open(filepath, 'r', encoding='utf-8') as file:
                return file.read()
        except Exception as e:
            logging.error(f"Failed to read context file {filepath}: {e}")
            return ""

    def is_chat_model(self, model_name: str) -> bool:
        """
        Check if the model is a chat model based on naming conventions.
        """
        # Adjust the logic as needed based on model naming conventions
        chat_models = {model.value for model in GptModelName}
        return model_name in chat_models

    def get_active_session(self, db: Session, user_id: int) -> ChatSession:
        now = datetime.now()
        active_session = db.query(ChatSession) \
            .filter(
            ChatSession.external_user_id == user_id,
            ChatSession.is_active == True,
            ChatSession.started_at >= now - timedelta(days=1)
        ).first()

        if active_session:
            return active_session
        else:
            new_session = ChatSession(
                is_active=True,
                started_at=datetime.now(),
                external_user_id=user_id
            )
            db.add(new_session)
            db.commit()
            db.refresh(new_session)
            return new_session

    def prepare_messages(self, initial_message: str, session: ChatSession) -> list:
        messages = [{"role": "system", "content": "You are a helpful assistant."}]
        history = session.get_conversation_history() if session.conversation_history else []
        messages.extend(history)
        messages.append({"role": "user", "content": initial_message})
        return messages

    async def ask_gpt(self, db: Session, preset_id: int, initial_message: str, user_id: int) -> Tuple[
        Optional[str], str, int]:
        preset = db.query(GptPreset).filter(GptPreset.id == preset_id).first()
        session = self.get_active_session(db, user_id)
        messages = self.prepare_messages(initial_message, session)

        response = self.gpt_chat_request(messages, preset)
        if response.choices and response.choices[0].message:
            message_content = response.choices[0].message.content
            current_history = session.get_conversation_history()
            current_history.append({"role": "assistant", "content": message_content})
            session.set_conversation_history(current_history)
            db.commit()
            return message_content, response.id, user_id
        else:
            return None, "Failed to get a valid response from OpenAI."

    def gpt_chat_request(self, messages, preset):
        return self.client.chat.completions.create(
            model=preset.model,
            messages=messages,
            temperature=preset.temperature,
            max_tokens=preset.max_tokens,
        )

    async def get_gpt_preset_by_course_id(self, db: Session, course_id: int) -> GptPreset:
        preset = db.query(GptPreset).filter(GptPreset.course_id == course_id).first()
        return preset
