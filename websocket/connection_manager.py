import json
import logging
from datetime import datetime
import aio_pika
from fastapi import WebSocket


class ConnectionManager:
    _instance = None

    def __new__(cls, rabbitmq_url: str = None):
        if cls._instance is None:
            cls._instance = super(ConnectionManager, cls).__new__(cls)
            logging.info(f"ConnectionManager initialized with RabbitMQ URL: {rabbitmq_url}")
            cls._instance.rabbitmq_url = rabbitmq_url
            cls._instance.rabbitmq_connection = None
            cls._instance.channel = None
            cls._instance.active_connections = {}
        return cls._instance

    async def connect_to_rabbitmq(self):
        logging.info("Connecting to RabbitMQ")
        if not self.rabbitmq_connection:
            self.rabbitmq_connection = await aio_pika.connect_robust(self.rabbitmq_url)
            self.channel = await self.rabbitmq_connection.channel()

    async def subscribe_to_course(self, course_name: str, websocket: WebSocket):
        logging.info(f"WebSocket connection for course ID {course_name}")
        if course_name not in self.active_connections:
            self.active_connections[course_name] = set()
            # Subscribe to RabbitMQ queue for the course
            await self.setup_rabbitmq_subscription(course_name)
        self.active_connections[course_name].add(websocket)

    async def setup_rabbitmq_subscription(self, course_name: str):
        logging.info(f"Setting up RabbitMQ subscription for course ID {course_name}")
        # Ensure connection and channel are established
        await self.connect_to_rabbitmq()
        queue_name = f'course_chat_{course_name}'
        queue = await self.channel.declare_queue(queue_name, durable=True)
        await queue.bind(self.channel.default_exchange, routing_key=queue_name)

        async for message in queue:
            async with message.process():
                # Dispatch message to all connected WebSockets for this course
                await self.dispatch_message(course_name, message.body.decode())

    async def dispatch_message(self, course_name: str, message: str):
        logging.info(f"Dispatching message to course ID {course_name}")
        if course_name in self.active_connections:
            for websocket in self.active_connections[course_name]:
                await websocket.send_text(message)

    async def disconnect(self, websocket: WebSocket, course_name: str):
        logging.info(f"Disconnecting WebSocket for course ID {course_name}")
        if course_name in self.active_connections and websocket in self.active_connections[course_name]:
            self.active_connections[course_name].remove(websocket)
            if not self.active_connections[course_name]:
                del self.active_connections[course_name]
                # Optionally, unsubscribe from the RabbitMQ queue if no more listeners

    async def send_message(self, course_name: str, message: str, sender: str):
        logging.info(f"Sending message to course ID {course_name}")
        formatted_message = self.format_message(message, sender)
        # Ensure connection and channel are established
        await self.connect_to_rabbitmq()
        # Publish to RabbitMQ
        await self.channel.default_exchange.publish(
            aio_pika.Message(body=formatted_message.encode()),
            routing_key=f'course_chat_{course_name}'
        )

    def format_message(self, message: str, sender: str) -> str:
        message_data = {
            "sender": sender,
            "message": message,
            "timestamp": datetime.utcnow().isoformat()
        }
        return json.dumps(message_data)
