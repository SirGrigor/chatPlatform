from fastapi import APIRouter, WebSocket, Depends

from core.config import settings
from core.exceptions import WebSocketAuthException
from websocket.connection_manager import ConnectionManager
from services.jwt_manager import verify_token
from db.session import get_db
from sqlalchemy.orm import Session

router = APIRouter()
manager = ConnectionManager(rabbitmq_url=settings.RABBITMQ_URL)


@router.websocket("/ws/{course_id}/{token}")
async def websocket_endpoint(websocket: WebSocket, course_id: int, token: str, db: Session = Depends(get_db)):
    try:
        # Attempt to verify the JWT token
        payload = verify_token(token)
        # If verification passes, connect the user
        await manager.connect(websocket)
        await manager.broadcast(f"User connected to course {course_id}")

        # Communication loop
        while True:
            data = await websocket.receive_text()
            await manager.send_message(course_id, data, payload)  # Assume send_message is adapted to use payload
    except WebSocketAuthException as auth_exc:
        # Handle authentication errors specifically
        await websocket.close(code=4001)  # Use appropriate WebSocket close code
        return
    except Exception as e:
        # Handle generic exceptions
        await websocket.close(code=1011)  # Unexpected condition
    finally:
        # Ensure disconnection is handled gracefully
        await manager.disconnect(websocket)
