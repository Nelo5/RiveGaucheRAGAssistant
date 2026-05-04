from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.db import get_db
from app.core.deps import require_user
from app.services import chat_service
from uuid import UUID
from app.schemas.chat import ChatResponse, MessageCreate, MessageResponse

router = APIRouter(prefix="/chats", tags=["Chats"])


@router.post("", response_model=ChatResponse, responses={401: {"description": "Not authenticated"}})
def create_chat(
    db: Session = Depends(get_db),
    current_user=Depends(require_user)
):
    return chat_service.create_chat(
        db=db,
        user_id=current_user.id,
    )


@router.get("", response_model=List[ChatResponse], responses={401: {"description": "Not authenticated"}})
def get_my_chats(
    db: Session = Depends(get_db),
    current_user=Depends(require_user)
):
    return chat_service.get_user_chats(
        db=db,
        user_id=current_user.id
    )


@router.get("/{chat_id}/messages", response_model=List[MessageResponse],
            responses={401: {"description": "Not authenticated"}, 404: {"description": "Chat not found"}})
def get_messages(
    chat_id: UUID,
    db: Session = Depends(get_db),
    current_user=Depends(require_user)
):
    return chat_service.get_chat_messages(db=db, chat_id=chat_id, user_id=current_user.id)

@router.post("/{chat_id}/messages", response_model=MessageResponse,
             responses={401: {"description": "Not authenticated"}, 404: {"description": "Chat not found"}, 400: {"description": "Malformed JSON body"}})
def send_message(
    chat_id: UUID,
    data: MessageCreate,
    db: Session = Depends(get_db),
    current_user=Depends(require_user)
):
    return chat_service.send_message(db=db, chat_id=chat_id, content=data.content, user_id=current_user.id)