import logging
from typing import Optional, Tuple, Any

import openai
from openai import OpenAI
from fastapi import HTTPException
from sqlalchemy.orm import Session

from core.config import settings
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

    async def ask_gpt_with_preset(self, db: Session, preset_id: int, prompt: str,
                                  context_file: Optional[str] = None) -> Tuple[Optional[str], str]:
        preset = self.get_gpt_preset(db, preset_id)
        if not preset:
            raise ValueError("Preset not found")

        # Correctly use the model name from the preset
        model = GptModelName[
            preset.model].value if preset.model in GptModelName._value2member_map_ else GptModelName.DAVINCI.value
        context = self._get_context_from_file(context_file) if context_file else None
        response = await self.ask_gpt(prompt, model, preset.max_tokens, preset.temperature, context)
        return response

    # Include the rest of the GptChatService methods here...

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

    async def ask_gpt(self, db: Session, preset_id: int, initial_message: str) -> Tuple[Optional[str], str]:
        preset = self.get_gpt_preset(db, preset_id)
        if not preset:
            raise ValueError("Preset not found")

        if self.is_chat_model(preset.model):
            try:
                response = self.client.chat.completions.create(
                    model=preset.model,
                    messages=[
                        {"role": "system", "content": "You are a helpful assistant."},
                        {"role": "user", "content": initial_message}
                    ],
                    temperature=preset.temperature,
                    max_tokens=preset.max_tokens,
                )
                # Extract and return the message content correctly
                if response.choices and response.choices[0].message:
                    message_content = response.choices[0].message.content
                    return message_content, response.id
                else:
                    return None, "Failed to get a valid response from OpenAI."
            except Exception as e:
                logging.error(f"OpenAI API error: {e}")
                raise HTTPException(status_code=500, detail="OpenAI API error.")
        else:
            return None, "The specified model is not supported for chat completions."