from enum import Enum
from typing import List

from pydantic import BaseModel


class ModelInfo(BaseModel):
    name: str
    max_tokens: int
    temperature_min: float = 0.0
    temperature_max: float = 1.0
    description: str = ""


class GptModelName(Enum):
    GPT4_0125_PREVIEW = "gpt-4-0125-preview"
    GPT4_TURBO_PREVIEW = "gpt-4-turbo-preview"
    GPT4_1106_PREVIEW = "gpt-4-1106-preview"
    GPT4_VISION_PREVIEW = "gpt-4-vision-preview"
    GPT4 = "gpt-4"
    GPT4_0613 = "gpt-4-0613"
    GPT4_32K = "gpt-4-32k"
    GPT4_32K_0613 = "gpt-4-32k-0613"
    GPT3_5_TURBO_0125 = "gpt-3.5-turbo-0125"
    GPT3_5_TURBO = "gpt-3.5-turbo"
    GPT3_5_TURBO_1106 = "gpt-3.5-turbo-1106"
    GPT3_5_TURBO_INSTRUCT = "gpt-3.5-turbo-instruct"
    GPT3_5_TURBO_16K = "gpt-3.5-turbo-16k"
    GPT3_5_TURBO_0613 = "gpt-3.5-turbo-0613"
    GPT3_5_TURBO_16K_0613 = "gpt-3.5-turbo-16k-0613"


class GptPresetCreate(BaseModel):
    name: str
    model: GptModelName
    max_tokens: int = 150
    temperature: float = 0.7
    course_id: int  # Add this line


class GptPresetResponseSchema(BaseModel):
    id: int
    name: str
    model: str
    max_tokens: int
    temperature: float
    course_id: int  # Add this line

    class Config:
        orm_mode = True


class ChatRequest(BaseModel):
    preset_id: int
    initial_message: str
    user_id: int


class ChatResponse(BaseModel):
    message: str
    response_id: str
    user_id: int


class GptModelDetailsResponse(BaseModel):
    models: List[ModelInfo]


def get_model_details() -> List[ModelInfo]:
    models = [
        ModelInfo(name="gpt-4-0125-preview", max_tokens=4096, temperature_min=0.0,
                  temperature_max=1.0, description="GPT-4 0125 Preview with advanced capabilities."),

        ModelInfo(name="gpt-4-turbo-preview", max_tokens=4096, temperature_min=0.0,
                  temperature_max=1.0,
                  description="GPT-4 Turbo Preview with enhanced response accuracy."),
        ModelInfo(name="gpt-4-1106-preview", max_tokens=4096, temperature_min=0.0,
                  temperature_max=1.0,
                  description="GPT-4 1106 Preview, featuring improved instruction following."),
        ModelInfo(name="gpt-4-vision-preview", max_tokens=4096, temperature_min=0.0,
                  temperature_max=1.0,
                  description="GPT-4 Vision Preview, capable of understanding images."),
        ModelInfo(name="gpt-4", max_tokens=8192, temperature_min=0.0, temperature_max=1.0,
                  description="GPT-4, offering broad capabilities and deep understanding."),
        ModelInfo(name="gpt-4-0613", max_tokens=8192, temperature_min=0.0, temperature_max=1.0,
                  description="Snapshot of GPT-4 from June 13th, 2023."),
        ModelInfo(name="gpt-4-32k", max_tokens=32768, temperature_min=0.0, temperature_max=1.0,
                  description="GPT-4 model with extended context window of 32k tokens."),
        ModelInfo(name="gpt-4-32k-0613", max_tokens=32768, temperature_min=0.0, temperature_max=1.0,
                  description="Snapshot of GPT-4 32k from June 13th, 2023."),
        ModelInfo(name="gpt-3.5-turbo-0125", max_tokens=4096, temperature_min=0.0,
                  temperature_max=1.0,
                  description="Updated GPT-3.5 Turbo model with higher accuracy."),
        ModelInfo(name="gpt-3.5-turbo", max_tokens=4096, temperature_min=0.0, temperature_max=1.0,
                  description="GPT-3.5 Turbo with improved accuracy."),
        ModelInfo(name="gpt-3.5-turbo-1106", max_tokens=4096, temperature_min=0.0,
                  temperature_max=1.0,
                  description="GPT-3.5 Turbo model with enhanced instruction following."),
        ModelInfo(name="gpt-3.5-turbo-instruct", max_tokens=4096, temperature_min=0.0,
                  temperature_max=1.0,
                  description="GPT-3.5 Turbo Instruct, compatible with legacy completions."),
        ModelInfo(name="gpt-3.5-turbo-16k", max_tokens=16385, temperature_min=0.0,
                  temperature_max=1.0,
                  description="Legacy GPT-3.5 Turbo model with 16k context window."),
        ModelInfo(name="gpt-3.5-turbo-0613", max_tokens=4096, temperature_min=0.0,
                  temperature_max=1.0,
                  description="Snapshot of GPT-3.5 Turbo from June 13th, 2023."),
        ModelInfo(name="gpt-3.5-turbo-16k-0613", max_tokens=16385, temperature_min=0.0,
                  temperature_max=1.0,
                  description="Snapshot of GPT-3.5 16k Turbo from June 13th, 2023."),
    ]
    return models


class PresetResponse(BaseModel):
    id: int
    name: str
    model: str
    max_tokens: int
    temperature: float
    course_id: int  # Ensure this represents the intended field; the duplicate has been removed for clarity.

    class Config:
        orm_mode = True


class PresetSchemasResponse:
    presets: List[PresetResponse]
    total: int
