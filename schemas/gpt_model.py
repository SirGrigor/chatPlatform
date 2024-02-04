from pydantic import BaseModel
from enum import Enum


class GptModelName(Enum):
    DAVINCI = "text-davinci-003"
    CURIE = "text-curie-001"
    BABBAGE = "text-babbage-001"
    ADA = "text-ada-001"


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
