from datetime import datetime
from pydantic import BaseModel, Field
from typing import List
from uuid import UUID


class MessageCreate(BaseModel):
    """Схема для отправки нового сообщения в существующий чат."""
    content: str = Field(
        ...,
        min_length=1,
        max_length=5000,
        description="Текст сообщения пользователя"
    )


class ChatResponse(BaseModel):
    """Схема ответа с информацией о чате."""
    id: UUID
    user_id: UUID
    title: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True 


class MessageResponse(BaseModel):
    """Схема ответа с информацией о сообщении."""
    id: UUID
    chat_id: UUID
    role: str  
    content: str
    created_at: datetime

    class Config:
        from_attributes = True