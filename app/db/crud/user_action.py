from sqlalchemy.orm import Session
from sqlalchemy import or_, and_, union_all

from fastapi import HTTPException
from datetime import datetime, timezone

from db.models import user_model
from db.schemas import user_schema, auth_schema
#from utils.jwt import Permission


async def create_user(db: Session, user: user_schema.UserCreate):
    """새로운 사용자를 생성합니다."""
    db_user = user_model.User(
        username=user.username,
        email=user.email,
        nickname=user.nickname,
        hashed_password=hash.hash_text(user.password),
        created_at=datetime.now(timezone.utc)
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

async def create_jwt(db: Session, user_id: int, access_token: str, refresh_token: str):
    db_token = user_model.JwtToken(
        user_id=user_id,
        access_token=access_token,
        refresh_token=refresh_token
    )
    db.add(db_token)
    db.commit()
    db.refresh(db_token)
    
    return db_token

def find_user_by_employee_id(db: Session, employee_id: str):
    return db.query(user_model.User).filter(user_model.User.employee_id == employee_id).first()

def find_user_by_user_id(db: Session, user_id: int):
    return db.query(user_model.User).filter(user_model.User.id == user_id).first()

def find_jwt_by_user_id(db: Session, user_id: int):
    return db.query(user_model.JwtToken).filter(user_model.JwtToken.user_id == user_id).first()