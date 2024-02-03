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

# CORS Middleware setup to allow any origin
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows any machine to send requests
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include your API router
app.include_router(api_router)

# Connection manager instance for RabbitMQ
manager = ConnectionManager(rabbitmq_url=settings.RABBITMQ_URL)


# Startup event handler to connect to RabbitMQ
@app.on_event("startup")
async def startup_event():
    await manager.connect_to_rabbitmq()


# Main entry point for running the application with Uvicorn
if __name__ == "__main__":
    logger.debug("Starting the application")
    uvicorn.run(
        app="main:app",  # Ensure this points to the correct app instance and module
        host="0.0.0.0",  # Listen on all network interfaces
        port=8000,  # Default port is 8000; change if needed
    )
