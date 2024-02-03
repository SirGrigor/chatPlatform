import json
from datetime import datetime
import aio_pika
from fastapi import WebSocket
from typing import Dict, Set


class ConnectionManager:
    def __init__(self, rabbitmq_url: str):
        self.rabbitmq_url = rabbitmq_url
        self.rabbitmq_connection = None
        self.channel = None
        # Maps course_id to a set of WebSockets interested in that course
        self.active_connections: Dict[int, Set[WebSocket]] = {}

    async def connect_to_rabbitmq(self):
        if not self.rabbitmq_connection:
            self.rabbitmq_connection = await aio_pika.connect_robust(self.rabbitmq_url)
            self.channel = await self.rabbitmq_connection.channel()

    async def subscribe_to_course(self, course_id: int, websocket: WebSocket):
        if course_id not in self.active_connections:
            self.active_connections[course_id] = set()
            # Subscribe to RabbitMQ queue for the course
            await self.setup_rabbitmq_subscription(course_id)
        self.active_connections[course_id].add(websocket)

    async def setup_rabbitmq_subscription(self, course_id: int):
        # Ensure connection and channel are established
        await self.connect_to_rabbitmq()
        queue_name = f'course_chat_{course_id}'
        queue = await self.channel.declare_queue(queue_name, durable=True)
        await queue.bind(self.channel.default_exchange, routing_key=queue_name)

        async for message in queue:
            async with message.process():
                # Dispatch message to all connected WebSockets for this course
                await self.dispatch_message(course_id, message.body.decode())

    async def dispatch_message(self, course_id: int, message: str):
        if course_id in self.active_connections:
            for websocket in self.active_connections[course_id]:
                await websocket.send_text(message)

    async def disconnect(self, websocket: WebSocket, course_id: int):
        if course_id in self.active_connections and websocket in self.active_connections[course_id]:
            self.active_connections[course_id].remove(websocket)
            if not self.active_connections[course_id]:
                del self.active_connections[course_id]
                # Optionally, unsubscribe from the RabbitMQ queue if no more listeners

    async def send_message(self, course_id: int, message: str, sender: str):
        formatted_message = self.format_message(message, sender)
        # Ensure connection and channel are established
        await self.connect_to_rabbitmq()
        # Publish to RabbitMQ
        await self.channel.default_exchange.publish(
            aio_pika.Message(body=formatted_message.encode()),
            routing_key=f'course_chat_{course_id}'
        )

    def format_message(self, message: str, sender: str) -> str:
        message_data = {
            "sender": sender,
            "message": message,
            "timestamp": datetime.utcnow().isoformat()
        }
        return json.dumps(message_data)
