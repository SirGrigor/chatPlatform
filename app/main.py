from fastapi import FastAPI
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api_v1.api import api_router
from core.config import settings
from websocket.connection_manager import ConnectionManager

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)
manager = ConnectionManager(rabbitmq_url=settings.RABBITMQ_URL)


@app.on_event("startup")
async def startup_event():
    # Connect to RabbitMQ when the application starts
    await manager.connect_to_rabbitmq()


def create_application() -> FastAPI:
    application = FastAPI(title="Learning Platform Chat", version="1.0")
    application.include_router(api_router)
    return application


app = create_application()
