from jose import jwt, JWTError, ExpiredSignatureError
from datetime import datetime, timedelta, timezone
from core.config import get_settings
from fastapi import HTTPException, Depends
from typing import List
from sqlalchemy.orm import Session

from core.etc import KST
from db.session import get_db

from enum import Enum

class Permission(Enum):
    ADMIN = "*"
    MODERATOR = "mod"
    USER = "-"

# Enccode
def encode_token(
    subject: str,
    user_id: int,
    secret_key: str,
    expries_delta: timedelta = None,
    permission: Permission = Permission.USER
    ) -> str:
    
    current_utc_time = datetime.now(KST)
    expire = current_utc_time + expries_delta if expries_delta else current_utc_time + timedelta(minutes=1)
    payload = { "sub": subject, "uid": user_id, "perm": permission.value, "iat": current_utc_time, "exp": expire }
    
    # Return JWT token
    return jwt.encode(payload, secret_key, algorithm="HS256")

def create_access_token(subject: str, user_id: int, permission: Permission = Permission.USER) -> str:
    return encode_token(subject, user_id, get_settings().access_secret_key, timedelta(days=7), permission)

def create_refresh_token(subject: str, user_id: int, permission: Permission = Permission.USER) -> str:
    return encode_token(subject, user_id, get_settings().refresh_secret_key, timedelta(days=30), permission)

# Decode
def decode_token(token: str, secret_key: str) -> dict:
    try:
        return jwt.decode(token, secret_key, algorithms=["HS256"])
    except ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token has expired")
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

def decode_access_token(token: str) -> dict:
    return decode_token(token, get_settings().access_secret_key)

def decode_refresh_token(token: str) -> dict:
    return decode_token(token, get_settings().refresh_secret_key)

def admin_decode_access_token(token: str) -> dict:
    payload = decode_access_token(token)
    if payload.get("perm") != Permission.ADMIN.value:
        raise HTTPException(status_code=403, detail="Permission denied")
    return payload