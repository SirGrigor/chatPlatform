import json
from datetime import datetime

import aio_pika
from fastapi import WebSocket


class ConnectionManager:
    def __init__(self, rabbitmq_url: str):
        self.rabbitmq_url = rabbitmq_url
        self.rabbitmq_connection = None
        self.channel = None

    def format_message(self, message: str, sender: str) -> str:
        message_data = {
            "sender": sender,
            "message": message,
            "timestamp": datetime.utcnow().isoformat()
        }
        return json.dumps(message_data)

    async def connect_to_rabbitmq(self):
        self.rabbitmq_connection = await aio_pika.connect_robust(self.rabbitmq_url)
        self.channel = await self.rabbitmq_connection.channel()

    async def send_message(self, course_id: int, message: str):
        if not self.channel:
            await self.connect_to_rabbitmq()
        await self.channel.default_exchange.publish(
            aio_pika.Message(body=message.encode()),
            routing_key=f'course_chat_{course_id}'
        )

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    async def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            await connection.send_text(message)

# Initialize and use this manager in your WebSocket endpoint
