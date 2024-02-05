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
from services.association_service import AssociationService
from services.course_service import get_course_id_by_name
from services.gpt_chat_service import GptChatService
from services.jwt_manager import verify_external_token
from websocket import connection_manager

gpt_chat_service = GptChatService()
router = APIRouter()
connection_manager = connection_manager.ConnectionManager(settings.RABBITMQ_URL)
active_connections: List[WebSocket] = []


async def get_or_create_external_user(db: Session, username: str, course_id: int) -> ExternalUser:
    user = db.query(ExternalUser).filter_by(username=username).first()
    association_service = AssociationService(db_session=db)  # Instantiate the service

    if not user:
        # Create a new ExternalUser instance
        user = ExternalUser(username=username, created_at=datetime.datetime.now(),
                            user_type="external")
        db.add(user)
        db.commit()
        # Use the instance to call the method
        association_service.add_association(user_id=user.id, course_id=course_id)

    else:
        # Use the instance to call the method
        if not association_service.check_association(user_id=user.id, course_id=course_id):
            association_service.add_association(user_id=user.id, course_id=course_id)

    return user


async def connect(websocket: WebSocket, user: ExternalUser):
    await websocket.accept()
    active_connections.append(websocket)


def disconnect(websocket: WebSocket):
    active_connections.remove(websocket)


@router.websocket("/ws/{token}")
async def websocket_endpoint(websocket: WebSocket, token: str, db: Session = Depends(get_db)):
    logging.info(f"WebSocket connection attempt with token: {token}")
    try:
        # Verify the token and get admin_id and user_type
        admin_id, user_type = await verify_external_token(token, db)
        if user_type != "external_admin":
            logging.warning("WebSocket connection attempt with invalid user type")
            await websocket.close(code=1008)
            return

        await connect(websocket, admin_id)
        # Receive initial setup message from the client
        setup_data = await websocket.receive_text()
        setup_data_json = json.loads(setup_data)

        # Extract username and course_name from the received setup_data_json
        username = setup_data_json.get('username')
        course_name = setup_data_json.get('course_name')

        # Validate received data
        if not username or not course_name:
            logging.error("Missing username or course_name in initial WebSocket message")
            await websocket.close(code=4000)  # Use an appropriate close code
            return

        # Use the extracted data
        course_id = await get_course_id_by_name(db, course_name)
        preset = await gpt_chat_service.find_gpt_preset_by_course_id(db, course_id)
        user = await get_or_create_external_user(db, username, course_id)
        # Assuming course_id is needed and can be derived from course_name in your application

        if not course_id:
            logging.error("Invalid course_name provided")
            await websocket.close(code=4000)  # Use an appropriate close code
            return

        try:
            while True:
                text_data = await websocket.receive_text()
                data_json = json.loads(text_data)
                message = data_json['message']

                response_message, response_id = await gpt_chat_service.ask_gpt(db, preset.id, message)
                print(response_message)
                if response_message:
                    await websocket.send_text(json.dumps({"message": response_message}))
                else:
                    await websocket.send_text(json.dumps({"error": "Failed to get response from GPT."}))
        except WebSocketDisconnect:
            disconnect(websocket)
    except WebSocketDisconnect:
        disconnect(websocket)
