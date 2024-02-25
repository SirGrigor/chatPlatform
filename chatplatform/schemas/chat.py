from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class ChatMessageCreate(BaseModel):
    sender_id: int
    message: str


class ChatMessageOut(ChatMessageCreate):
    timestamp: Optional[datetime] = None
