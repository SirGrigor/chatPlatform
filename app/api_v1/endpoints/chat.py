import datetime
import json
import logging
from typing import List

from fastapi import APIRouter, Depends, WebSocket, WebSocketDisconnect
from sqlalchemy.orm import Session

from core.config import settings
from db.models.external_user import ExternalUser
from db.session import get_db
from services.course_service import get_course_id_by_name
from services.jwt_manager import verify_external_token
from websocket import connection_manager

router = APIRouter()
connection_manager = connection_manager.ConnectionManager(settings.RABBITMQ_URL)
active_connections: List[WebSocket] = []


async def get_or_create_external_user(db: Session, username: str) -> ExternalUser:
    user = db.query(ExternalUser).filter_by(username=username).first()
    if not user:
        # Create a new ExternalUser instance
        user = ExternalUser(username=username, created_at=datetime.datetime.now(),
                            user_type="eternal")
        db.add(user)
        db.commit()
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

        await websocket.accept()

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
        user = await get_or_create_external_user(db, username)
        # Assuming course_id is needed and can be derived from course_name in your application
        course_id = await get_course_id_by_name(db, course_name)  # You need to implement this

        if not course_id:
            logging.error("Invalid course_name provided")
            await websocket.close(code=4000)  # Use an appropriate close code
            return

        await connection_manager.subscribe_to_course(course_id, websocket)

        while True:
            # Now handle other messages as usual
            data = await websocket.receive_text()
            data_json = json.loads(data)
            # Simplified message handling and dispatch
            await connection_manager.send_message(course_id, data_json['message'], admin_id)

    except WebSocketDisconnect:
        # Make sure to use course_id from the user object or another source if needed
        connection_manager.disconnect(websocket, course_id)
    except Exception as e:
        logging.error(f"Error in WebSocket connection: {e}")
        await websocket.close(code=1011)
