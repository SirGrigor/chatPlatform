import uvicorn
from fastapi import FastAPI
from fastapi.logger import logger
from fastapi.middleware.cors import CORSMiddleware
from app.api_v1.api import api_router
from core.config import settings
from websocket.connection_manager import ConnectionManager

app = FastAPI(
    title="Learning Platform Chat",
    version="1.0",
    ssl_keyfile=settings.SSL_KEY_FILE,
    ssl_certfile=settings.SSL_CERT_FILE,
)


app.add_middleware(
    CORSMiddleware,
    websockets=True,
    allow_origins=["https://localhost:8000, http://http://localhost:63342/"],  # Specify the origin where your frontend is hosted
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router)
manager = ConnectionManager(rabbitmq_url=settings.RABBITMQ_URL)


@app.on_event("startup")
async def startup_event():
    await manager.connect_to_rabbitmq()


def create_application() -> FastAPI:
    application = FastAPI(title="Learning Platform Chat", version="1.0")
    application.include_router(api_router)
    return application


app = create_application()

if __name__ == "__main__":
    logger.debug("Starting the application")
    uvicorn.run(
        "app:app",
        host="0.0.0.0",
        port=8000,
    )
