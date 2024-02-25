import json
import logging
from typing import List

from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends
from sqlalchemy.orm import Session

from chatplatform.core.config import settings
from chatplatform.db.models.external_user import ExternalUser
from chatplatform.db.session import DBSession
from chatplatform.services.course_service import CourseService
from chatplatform.services.jwt_manager import JWTManager
from chatplatform.services.websocket_service import WebSocketService
from chatplatform.websocket import connection_manager

router = APIRouter()
jwt_manager = JWTManager(DBSession().get_db())
connection_manager = connection_manager.ConnectionManager(settings.RABBITMQ_URL)
active_connections: List[WebSocket] = []


async def connect(websocket: WebSocket, user: ExternalUser):
    await websocket.accept()
    active_connections.append(websocket)


def disconnect(websocket: WebSocket):
    if websocket in active_connections:
        active_connections.remove(websocket)
    logging.info("WebSocket disconnected")


@router.websocket("/ws/{token}")
async def websocket_endpoint(websocket: WebSocket, token: str, db: Session = Depends(DBSession.get_db)):
    websocket_service = WebSocketService(db)
    course_service = CourseService(db)
    logging.info(f"WebSocket connection attempt with token: {token}")
    try:
        admin_id, user_type = await websocket_service.verify_external_token(token)
        if user_type != "external_admin":
            logging.warning("WebSocket connection attempt with invalid user type")
            await websocket.close(code=1008)
            return

        await connect(websocket, admin_id)
        setup_data = await websocket.receive_text()
        setup_data_json = json.loads(setup_data)

        username = setup_data_json.get('username')
        user = await websocket_service.get_or_create_external_user(username, admin_id)
        allocated_courses = await course_service.get_courses_by_admin_id(admin_id)

        while True:
            text_data = await websocket.receive_text()
            data_json = json.loads(text_data)
            message = data_json['message']

            # Use the WebSocketService to handle business logic
            async for response_chunk in websocket_service.generate_gpt_responses(message, allocated_courses):
                if response_chunk:
                    await websocket.send_text(json.dumps({"message": response_chunk}))
                else:
                    await websocket.send_text(json.dumps({"error": "Failed to get response from GPT."}))
                    break
    except WebSocketDisconnect:
        disconnect(websocket)
        logging.info("WebSocket connection closed")
