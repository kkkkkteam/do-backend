from fastapi import APIRouter
from api import users
from core.config import Settings

router = APIRouter()

router.include_router(users.router, tags=["users"], prefix="/users")
