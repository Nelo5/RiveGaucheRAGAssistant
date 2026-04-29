import uuid
from sqlalchemy import Column, Text, String, ForeignKey, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func

from app.core.db import Base


class Message(Base):
    __tablename__ = "messages"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    chat_id = Column(
        UUID(as_uuid=True),
        ForeignKey("chats.id"),
        nullable=False
    )

    role = Column(String, nullable=False) 
    content = Column(Text, nullable=False)

    created_at = Column(DateTime(timezone=True), server_default=func.now())