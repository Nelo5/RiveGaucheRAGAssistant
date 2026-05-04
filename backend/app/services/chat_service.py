from uuid import UUID

from sqlalchemy.orm import Session
from fastapi import HTTPException
from app.models.chat import Chat
from app.models.message import Message
from app.services.rag_service import rag_service




def create_chat(db: Session, user_id:UUID):
    chat_count = db.query(Chat).filter(Chat.user_id == user_id).count()
    chat_number = chat_count + 1
    title = f"Чат {chat_number}"

    chat = Chat(user_id=user_id, title=title)
    db.add(chat)
    db.commit()
    db.refresh(chat)

    return chat


def get_user_chats(db: Session, user_id:UUID):

    return db.query(Chat).filter(
        Chat.user_id == user_id
    ).order_by(Chat.updated_at.desc()).all()


def get_chat_messages(db: Session, chat_id:UUID, user_id:UUID):

    chat = db.query(Chat).filter(
        Chat.id == chat_id,
        Chat.user_id == user_id
    ).first()

    if not chat:
        raise HTTPException(status_code=404, detail="Chat not found or access denied")

    return db.query(Message).filter(
        Message.chat_id == chat_id
    ).order_by(Message.created_at.asc()).all()


def send_message(db: Session, chat_id: UUID, content: str, user_id: str):
    chat = db.query(Chat).filter(Chat.id == chat_id, Chat.user_id == user_id).first()
    if not chat:
        raise HTTPException(status_code=404, detail="Chat not found or access denied")

    previous_messages = db.query(Message).filter(Message.chat_id == chat_id).order_by(Message.created_at.asc()).all()
    history = [{"role": m.role, "content": m.content} for m in previous_messages[-10:]]


    user_msg = Message(chat_id=chat_id, role="user", content=content)
    db.add(user_msg)
    db.commit()

    answer = rag_service.ask(content, history=history)

    ai_msg = Message(chat_id=chat_id, role="assistant", content=answer)
    db.add(ai_msg)
    db.commit()
    return ai_msg