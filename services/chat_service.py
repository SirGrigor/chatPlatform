from sqlalchemy.orm import Session
from db.models import message as Message
from typing import List


def save_message(db: Session, session_id: int, sender_id: int, message: str) -> Message:
    db_message = Message(session_id=session_id, sender_id=sender_id, text=message)
    db.add(db_message)
    db.commit()
    db.refresh(db_message)
    return db_message


def get_chat_history(db: Session, session_id: int) -> List[Message]:
    return db.query(Message).filter(Message.session_id == session_id).all()
