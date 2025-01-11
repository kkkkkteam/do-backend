from fastapi import APIRouter
from api import auth, users, admin, experience
from core.config import Settings

api_v1_router = APIRouter(prefix="/api/v1")

api_v1_router.include_router(auth.router, tags=["auth"], prefix="/auth")
api_v1_router.include_router(users.router, tags=["users"], prefix="/users")

api_v1_router.include_router(admin.router, tags=["admin"], prefix="/admin")
api_v1_router.include_router(experience.router, tags=["experience"], prefix="/experience")