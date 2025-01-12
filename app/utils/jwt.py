from jose import jwt, JWTError, ExpiredSignatureError
from datetime import datetime, timedelta, timezone
from core.config import get_settings
from fastapi import HTTPException, Depends
from typing import List
from sqlalchemy.orm import Session

from core.etc import KST

from db.models import user_model, admin_model


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

def user_decode_access_token(db: Session, token: str) -> dict:
    if not db.query(user_model.UserJwtToken).filter(user_model.UserJwtToken.access_token == token).first():
        raise HTTPException(status_code=401, detail="Invalid token")
    
    # verification permission
    payload = decode_token(token, get_settings().access_secret_key)
    return payload

def user_decode_refresh_token(db: Session, token: str) -> dict:
    if not db.query(user_model.UserJwtToken).filter(user_model.UserJwtToken.refresh_token == token).first():
        raise HTTPException(status_code=401, detail="Invalid token")
    
    # verification permission
    payload = decode_token(token, get_settings().refresh_secret_key)
    if payload.get("perm") != Permission.USER.value:
        raise HTTPException(status_code=403, detail="Permission denied")
    
    return payload

def admin_decode_access_token(db: Session, token: str) -> dict:
    if not db.query(admin_model.AdminJwtToken).filter(admin_model.AdminJwtToken.access_token == token).first():
        raise HTTPException(status_code=401, detail="Invalid token")

    # verification permission
    payload = decode_token(token, get_settings().access_secret_key)
    if payload.get("perm") != Permission.ADMIN.value:
        raise HTTPException(status_code=403, detail="Permission denied")
    
    return payload

def admin_decode_refresh_token(db: Session, token: str) -> dict:
    if not db.query(admin_model.AdminJwtToken).filter(admin_model.AdminJwtToken.refresh_token == token).first():
        raise HTTPException(status_code=401, detail="Invalid token")

    # verification permission
    payload = decode_token(token, get_settings().refresh_secret_key)
    if payload.get("perm") != Permission.ADMIN.value:
        raise HTTPException(status_code=403, detail="Permission denied")
    
    return payload