from sqlalchemy.orm import Session
from sqlalchemy import or_, and_, union_all

from fastapi import HTTPException
from datetime import datetime, timezone

from db.models import user_model
from db.schemas import user_schema
from utils import hash

# Create
async def create_jwt(db: Session, user_id: int, data: user_schema.JwtToken) -> user_model.UserJwtToken:
    db_jwt = user_model.UserJwtToken(
        user_id=user_id,
        access_token=data.access_token,
        refresh_token=data.refresh_token
    )
    
    db.add(db_jwt)
    db.commit()
    db.refresh(db_jwt)
    
    return db_jwt

async def create_user(db: Session, data: user_schema.UserCreate) -> user_model.User:
    
    hashed_password = hash.hash_text(data.password)
    
    db_user = user_model.User(
        employee_id=data.employee_id,
        username=data.username,
        hashed_password=hashed_password,
        name=data.name,
        level=data.level,
        join_date=data.join_date,
        department=data.department
    )
    
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    return db_user

# Read
def find_user_by_employee_id(db: Session, employee_id: str) -> user_model.User:
    return db.query(user_model.User).filter(user_model.User.employee_id == employee_id).first()

def find_user_by_user_id(db: Session, user_id: int) -> user_model.User:
    return db.query(user_model.User).filter(user_model.User.id == user_id).first()

def find_jwt_by_user_id(db: Session, user_id: int) -> user_model.UserJwtToken:
    return db.query(user_model.UserJwtToken).filter(user_model.UserJwtToken.user_id == user_id).first()

# Update
async def update_jwt_token(db: Session, user_id: int, data: user_schema.JwtToken) -> user_model.UserJwtToken:
    db_jwt = db.query(user_model.UserJwtToken).filter(user_model.UserJwtToken.user_id == user_id).first()
    
    db_jwt.access_token = data.access_token
    db_jwt.refresh_token = data.refresh_token
    
    db.commit()
    db.refresh(db_jwt)

    return db_jwt

# Delete
