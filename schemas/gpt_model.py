from pydantic import BaseModel
from enum import Enum


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


class ChatResponse(BaseModel):
    message: str
    response_id: str


class GptModelListResponse(BaseModel):
    models: list[GptModelName]
