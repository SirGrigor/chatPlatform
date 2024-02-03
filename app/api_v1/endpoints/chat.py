import json
from typing import List

from fastapi import APIRouter, WebSocket, Depends
from jose import jwt
from sqlalchemy.orm import Session
from uvicorn import logging

from core.config import settings
from db.models.external_user import ExternalUser
from db.session import get_db
from services.jwt_manager import verify_external_token
from websocket import connection_manager

router = APIRouter()

active_connections: List[WebSocket] = []


async def get_or_create_external_user(db: Session, admin_id: str, username: str, course_id: str) -> ExternalUser:
    # You might need to adjust the logic here depending on how you're identifying users
    user = db.query(ExternalUser).filter_by(username=username, course_id=course_id).first()
    if not user:
        # Create a new ExternalUser instance
        user = ExternalUser(admin_id=admin_id, username=username, course_id=course_id)
        db.add(user)
        db.commit()
    return user


async def connect(websocket: WebSocket, user: ExternalUser):
    await websocket.accept()
    active_connections.append(websocket)


def disconnect(websocket: WebSocket):
    active_connections.remove(websocket)


@router.websocket("/ws/chat/{token}")
async def websocket_endpoint(websocket: WebSocket, token: str, db: Session = Depends(get_db)):
    admin_id, user_type = await verify_external_token(token, db)
    if user_type != "external_admin":
        await websocket.close(code=1008)
        return

    await websocket.accept()

    # Example of handling a message from the WebSocket client
    while True:
        data = await websocket.receive_text()
        data_json = json.loads(data)
        message = data_json.get("message")
        course_id = data_json.get("course_id")  # Assuming the course ID is part of the message

        # Publish the message to RabbitMQ
        await connection_manager.send_message(course_id, message)
