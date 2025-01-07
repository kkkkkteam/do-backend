from jose import jwt, JWTError
from datetime import datetime, timedelta, timezone
from core.config import get_settings
from fastapi import HTTPException, Depends
from typing import List
from sqlalchemy.orm import Session

from db.session import get_db
from db.crud.user import user_read

from enum import Enum

class Permission(Enum):
    ADMIN = "*"
    MODERATOR = "mod"
    USER = "-"

# Enccode
async def encode_token(
    subject: str,
    user_id: int,
    secret_key: str,
    expries_delta: timedelta = None,
    permission: Permission = Permission.USER
    ) -> str:
    
    current_utc_time = datetime.now(timezone.utc)
    expire = current_utc_time + expries_delta if expries_delta else current_utc_time + timedelta(minutes=1)
    payload = { "sub": subject, "uid": user_id, "perm": permission.value, "iat": current_utc_time, "exp": expire }
    
    # Return JWT token
    return jwt.encode(payload, secret_key, algorithm="HS256")

async def create_access_token(subject: str, user_id: int, permission: Permission = Permission.USER) -> str:
    return await encode_token(subject, user_id, get_settings().access_secret_key, timedelta(days=7), permission)

async def create_refresh_token(subject: str, user_id: int, permission: Permission = Permission.USER) -> str:
    return await encode_token(subject, user_id, get_settings().refresh_secret_key, timedelta(days=30), permission)

# Decode
async def decode_token(token: str, secret_key: str) -> dict:
    try:
        return jwt.decode(token, secret_key, algorithms=["HS256"])
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

async def get_payload(token: str, secret_key: str):
    return await decode_token(token, secret_key)