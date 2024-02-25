import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from chatplatform.core.config import settings
from chatplatform.core.config import logger


from chatplatform.app.api_v1.api import api_router
from chatplatform.websocket.connection_manager import ConnectionManager

app = FastAPI(
    title="Learning Platform Chat",
    version="1.0",
    ssl_keyfile=settings.SSL_KEY_FILE,
    ssl_certfile=settings.SSL_CERT_FILE,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows any machine to send requests
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router)

manager = ConnectionManager(rabbitmq_url=settings.RABBITMQ_URL)


@app.on_event("startup")
async def startup_event():
    await manager.connect_to_rabbitmq()


if __name__ == "__main__":
    logger.info("Starting server")
    uvicorn.run(
        app="main:app",  # Ensure this points to the correct app instance and module
        host="0.0.0.0",  # Listen on all network interfaces
        port=8000,  # Default port is 8000; change if needed
    )
