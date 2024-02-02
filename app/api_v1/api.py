from fastapi import APIRouter
from .endpoints import auth, chat, course, document, user

api_router = APIRouter()
api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
api_router.include_router(chat.router, prefix="/chat", tags=["Chat"])
api_router.include_router(course.router, prefix="/courses", tags=["Courses"])
api_router.include_router(document.router, prefix="/documents", tags=["Documents"])
api_router.include_router(user.router, prefix="/users", tags=["Users"])