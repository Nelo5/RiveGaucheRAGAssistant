from datetime import datetime
from pydantic import BaseModel, Field, field_validator
from typing import List
from uuid import UUID
import re

class MessageCreate(BaseModel):
    content: str = Field(..., min_length=1, max_length=5000, description="Текст сообщения пользователя")
    @field_validator("content")
    @classmethod
    def strip_whitespace(cls, v: str) -> str:
        return v.replace("\x00", "").strip()


class MessageResponse(BaseModel):
    """Схема ответа с информацией о сообщении."""
    id: UUID
    chat_id: UUID
    role: str  
    content: str
    created_at: datetime

    class Config:
        from_attributes = True


class ChatResponse(BaseModel):
    """Схема ответа с информацией о чате."""
    id: UUID
    user_id: UUID
    title: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True 
