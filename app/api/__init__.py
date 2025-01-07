from fastapi import APIRouter
from api import auth
from core.config import Settings

api_v1_router = APIRouter(prefix="/api/v1")

api_v1_router.include_router(auth.router, tags=["auth"], prefix="/auth")
