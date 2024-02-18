import datetime
import json
import logging
from typing import List

from fastapi import APIRouter, Depends, WebSocket, WebSocketDisconnect
from sqlalchemy.orm import Session

from core.config import settings
from db.models.external_user import ExternalUser
from db.session import get_db
from services import gpt_chat_service
from services.gpt_chat_service import GptChatService
from services.jwt_manager import verify_external_token
from websocket import connection_manager

gpt_chat_service = GptChatService()
router = APIRouter()
connection_manager = connection_manager.ConnectionManager(settings.RABBITMQ_URL)
active_connections: List[WebSocket] = []


async def get_or_create_external_user(db: Session, username: str) -> ExternalUser:
    user = db.query(ExternalUser).filter_by(username=username).first()

    if not user:
        # Create a new ExternalUser instance
        user = ExternalUser(username=username, created_at=datetime.datetime.now(),
                            user_type="external")
        db.add(user)
        db.commit()

    return user


async def connect(websocket: WebSocket, user: ExternalUser):
    await websocket.accept()
    active_connections.append(websocket)


def disconnect(websocket: WebSocket):
    if websocket in active_connections:
        active_connections.remove(websocket)
    logging.info("WebSocket disconnected")


@router.websocket("/ws/{token}")
async def websocket_endpoint(websocket: WebSocket, token: str, db: Session = Depends(get_db)):
    logging.info(f"WebSocket connection attempt with token: {token}")
    try:
        admin_id, user_type = await verify_external_token(token, db)
        if user_type != "external_admin":
            logging.warning("WebSocket connection attempt with invalid user type")
            await websocket.close(code=1008)
            return

        await connect(websocket, admin_id)
        setup_data = await websocket.receive_text()
        setup_data_json = json.loads(setup_data)

        username = setup_data_json.get('username')
        user = await get_or_create_external_user(db, username)

        while True:
            text_data = await websocket.receive_text()
            data_json = json.loads(text_data)
            message = data_json['message']

            # Stream GPT responses directly to the WebSocket client
            async for response_chunk in gpt_chat_service.ask_gpt(db, message, user.id):
                if response_chunk:
                    await websocket.send_text(json.dumps({"message": response_chunk}))
                else:
                    # If `response_chunk` is None, it indicates an error occurred
                    await websocket.send_text(json.dumps({"error": "Failed to get response from GPT."}))
                    break  # Exit the loop if an error occurred
    except WebSocketDisconnect:
        disconnect(websocket)
        logging.info("WebSocket connection closed")
