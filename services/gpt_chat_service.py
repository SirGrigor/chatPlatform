import logging
from datetime import datetime, timedelta

from openai import OpenAI
from sqlalchemy.orm import Session

from core.config import settings
from db.models.chat_session import ChatSession
from db.models.document import Document
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

    def prepare_messages(self, initial_message: str, session: ChatSession, documents) -> list:
        file_contents = [doc.document_content for doc in documents]
        file_context_message = "\n".join(file_contents)  # Combine all contents into a single string
        file_context_system_message = {"role": "system", "content": file_context_message}

        # Initialize messages list with file context at index 0.
        messages = [file_context_system_message, {"role": "system",
                                                  "content": "You are a helpful assistant. Note: If your question "
                                                             "cannot be answered through the file content, "
                                                             "I'll try to help based on my own knowledge. I aim to be "
                                                             "helpful yet discreet, focusing primarily on the "
                                                             "information you've provided."}]

        # Add a helpful assistant message.

        # Include conversation history if available.
        history = session.get_conversation_history() if session.conversation_history else []
        messages.extend(history)

        # Append the initial user message.
        messages.append({"role": "user", "content": initial_message})

        return messages

    async def ask_gpt(self, db: Session, preset_id: int, initial_message: str, user_id: int):
        preset = db.query(GptPreset).filter(GptPreset.id == preset_id).first()
        file_context = db.query(Document).filter(Document.course_id == preset.course.id).all()
        session = self.get_active_session(db, user_id)
        initial_message_size_bytes = len(initial_message.encode('utf-8'))

        if initial_message_size_bytes > 20480:
            session.clear_conversation_history()
            db.commit()

        messages = self.prepare_messages(initial_message, session, file_context)

        # Initially log the user's message in the conversation history
        current_history = session.get_conversation_history()
        current_history.append({"role": "user", "content": initial_message})
        session.set_conversation_history(current_history)
        db.commit()

        async for response in self.gpt_chat_request(messages, preset):
            print(response)  # Debug print to inspect the response structure
            if response.choices and response.choices[0].delta and response.choices[0].delta.content:
                chunk_content = response.choices[0].delta.content
                # Process each chunk: Append it to the conversation history and yield
                current_history = session.get_conversation_history()
                current_history.append({"role": "assistant", "content": chunk_content})
                session.set_conversation_history(current_history)
                db.commit()

                # Yield the chunk to the caller, which could be a WebSocket handler
                yield chunk_content
            else:
                # Handle the case where GPT fails to return a valid response
                yield None, ".", user_id



    async def gpt_chat_request(self, messages, preset):
        # Send the ChatCompletion request with streaming enabled
        response = self.client.chat.completions.create(
            model=preset.model,
            messages=messages,
            temperature=preset.temperature,
            max_tokens=preset.max_tokens,
            stream=True
        )

        # Iterate through the stream of responses
        for chunk in response:
            yield chunk

    async def get_gpt_preset_by_course_id(self, db: Session, course_id: int) -> GptPreset:
        preset = db.query(GptPreset).filter(GptPreset.course_id == course_id).first()
        return preset
