from fastapi import APIRouter
from api import common

api_v1_router = APIRouter(prefix="/api/v1")

# common
api_v1_router.include_router(common.router, tags=["common"], prefix="/common")

