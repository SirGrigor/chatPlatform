import logging
from typing import Optional

import openai
from fastapi import HTTPException
from sqlalchemy.orm import Session

from core.config import settings
from db.models.gpt_preset import GptPreset
from schemas.gpt_model import GptModelName

openai_service = openai


class GptChatService:
    def __init__(self):
        openai.api_key = settings.OPENAPI_KEY

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
                                  context_file: Optional[str] = None) -> str:
        preset = self.get_gpt_preset(db, preset_id)
        if not preset:
            raise ValueError("Preset not found")

        # Correctly use the model name from the preset
        model = GptModelName[
            preset.model].value if preset.model in GptModelName._value2member_map_ else GptModelName.DAVINCI.value
        context = self._get_context_from_file(context_file) if context_file else None

        return await self.ask_gpt(prompt, model, preset.max_tokens, preset.temperature, context)

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

    async def ask_gpt(self, db: Session, preset_id: int, initial_message: str) -> str:
        preset = self.get_gpt_preset(db, preset_id)
        if not preset:
            raise ValueError("Preset not found")

        try:
            response = openai_service.chat.completions.create(
                model=preset.model,  # Ensure this is a valid GPT-3.5-turbo or similar model
                messages=[
                    {"role": "system", "content": "You are a helpful assistant."},
                    {"role": "user", "content": initial_message}
                ],
                temperature=preset.temperature,
                max_tokens=preset.max_tokens,
            )
            if response and response['choices']:
                return response['choices'][0]['message']['content'].strip()
            else:
                return "Failed to get a valid response from OpenAI."
        except openai.OpenAIError as e:
            logging.error(f"OpenAI API error: {e}")
            raise HTTPException(status_code=500, detail="OpenAI API error.")
        except Exception as e:
            logging.error(f"Unexpected error: {e}")
            raise HTTPException(status_code=500, detail="An unexpected error occurred.")