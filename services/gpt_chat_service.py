import logging
from typing import Optional

import openai
from sqlalchemy.orm import Session

from core.config import settings
from db.models.gpt_preset import GptPreset
from schemas.gpt_model import GptModelName


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

    async def ask_gpt(self, db, preset_id: int, initial_message: str) -> str:
        """
        Sends a prompt to the GPT model and returns the response.
        """
        preset = self.get_gpt_preset(db, preset_id)

        try:
            response = openai.Completion.create(
                engine=preset.model,
                context=preset.context,
                prompt=initial_message,
                max_tokens=preset.max_tokens,
                temperature=preset.temperature,
                n=1,
                stop=None,
                top_p=1.0,
                frequency_penalty=0.0,
                presence_penalty=0.0,
            )
            return response.choices[0].text.strip()
        except openai.OpenAIError as e:
            logging.error(f"OpenAI API error: {e}")
            return "An error occurred while processing your request. Please try again."
        except Exception as e:
            logging.error(f"Unexpected error: {e}")
            return "An unexpected error occurred. Please try again."
