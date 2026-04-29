from sqlalchemy.orm import Session

from app.models.chat import Chat
from app.models.message import Message
from app.services.rag_service import rag_service





def create_chat(db: Session, user_id):
    chat_count = db.query(Chat).filter(Chat.user_id == user_id).count()
    chat_number = chat_count + 1
    title = f"Чат {chat_number}"

    chat = Chat(user_id=user_id, title=title)
    db.add(chat)
    db.commit()
    db.refresh(chat)

    return chat


def get_user_chats(db: Session, user_id):

    return db.query(Chat).filter(
        Chat.user_id == user_id
    ).order_by(Chat.updated_at.desc()).all()


def get_chat_messages(db: Session, chat_id, user_id):

    chat = db.query(Chat).filter(
        Chat.id == chat_id,
        Chat.user_id == user_id
    ).first()

    if not chat:
        return None

    return db.query(Message).filter(
        Message.chat_id == chat_id
    ).order_by(Message.created_at.asc()).all()


def send_message(db: Session, chat_id, content: str):

    history = []
    previous_messages = db.query(Message).filter(
        Message.chat_id == chat_id
    ).order_by(Message.created_at.asc()).all()


    user_msg = Message(chat_id=chat_id, role="user", content=content)
    db.add(user_msg)
    db.commit()

    for msg in previous_messages[-10:]: 
        history.append({"role": msg.role, "content": msg.content})

    answer = rag_service.ask(content, history=history)

    ai_msg = Message(chat_id=chat_id, role="assistant", content=answer)
    db.add(ai_msg)
    db.commit()

    return ai_msg