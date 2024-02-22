from fastapi import APIRouter
from .endpoints import auth, websocket, course, document, gpt_preset

api_router = APIRouter()
api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
api_router.include_router(course.router, prefix="/courses", tags=["Courses"])
api_router.include_router(document.router, prefix="/documents", tags=["Documents"])
api_router.include_router(gpt_preset.router, prefix="/preset", tags=["Preset"])
api_router.include_router(websocket.router, prefix="/chat", tags=["Chat"])
