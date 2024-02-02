from datetime import datetime

from fastapi import APIRouter, WebSocket, Depends, HTTPException
from jose import JWTError
from sqlalchemy.orm import Session
from starlette.websockets import WebSocketDisconnect

from db.models.user import User
from db.session import get_db
from schemas.chat import ChatMessageOut
from typing import List
import json

from services.jwt_manager import verify_token

router = APIRouter()

active_connections: List[WebSocket] = []


async def get_current_user(websocket: WebSocket, token: str = None, db: Session = Depends(get_db)) -> User:
    if token is None:
        await websocket.close(code=4001)
        raise HTTPException(status_code=400, detail="Missing token")
    try:
        payload = verify_token(token)
        user_id = payload.get("user_id")
        user = db.query(User).filter(User.id == user_id).first()
        if user is None:
            await websocket.close(code=4002)
            raise HTTPException(status_code=404, detail="User not found")
        return user
    except JWTError:
        await websocket.close(code=4003)
        raise HTTPException(status_code=401, detail="Invalid token")


async def connect(websocket: WebSocket, user: User):
    await websocket.accept()
    active_connections.append(websocket)


def disconnect(websocket: WebSocket):
    active_connections.remove(websocket)


@router.websocket("/ws/chat/{token}")
async def websocket_endpoint(websocket: WebSocket, token: str, db: Session = Depends(get_db)):
    user = await get_current_user(websocket, token, db)
    await connect(websocket, user)
    try:
        while True:
            data = await websocket.receive_text()
            message = ChatMessageOut(sender_id=user.id, message=data, timestamp=datetime.now())
            await broadcast(json.dumps(message.dict()))
    except WebSocketDisconnect:
        disconnect(websocket)


async def broadcast(message: str):
    for connection in active_connections:
        await connection.send_text(message)
