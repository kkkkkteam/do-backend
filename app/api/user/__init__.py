from fastapi import APIRouter
from api.user import user, auth

api_v1_router = APIRouter(prefix="/api/v1")

# admin
api_v1_router.include_router(user.router, tags=["user"], prefix="/user")
api_v1_router.include_router(auth.router, tags=["user/auth"], prefix="/user/auth")


