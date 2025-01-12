from sqlalchemy.orm import Session
from sqlalchemy import or_, and_, union_all

from fastapi import HTTPException
from datetime import datetime, timezone

from db.schemas import admin_schema
from db.models import admin_model

from core.etc import KST

from utils import hash

async def create_admin(db: Session, data: admin_schema.AdminCreate) -> admin_model.Admin:
    
    hashed_password = hash.hash_text(data.password)

    db_admin = admin_model.Admin(
        username=data.username,
        hashed_password=hashed_password,
        created_at=datetime.now(KST)
    )
    
    db.add(db_admin)
    db.commit()
    db.refresh(db_admin)
    
    return db_admin

async def create_admin_jwt(db: Session, admin_id: int, data: admin_schema.AdminJwtToken) -> admin_model.AdminJwtToken:
    db_jwt = admin_model.AdminJwtToken(
        admin_id=admin_id,
        access_token=data.access_token,
        refresh_token=data.refresh_token
    )
    
    db.add(db_jwt)
    db.commit()
    db.refresh(db_jwt)
    
    return db_jwt

def find_admin_by_username(db: Session, username: str) -> admin_model.Admin:
    return db.query(admin_model.Admin).filter(admin_model.Admin.username == username).first()

def find_admin_jwt_by_admin_id(db: Session, admin_id: int) -> admin_model.AdminJwtToken:
    return db.query(admin_model.AdminJwtToken).filter(admin_model.AdminJwtToken.admin_id == admin_id).first()


async def update_admin_jwt_token(db: Session, admin_id: int, data: admin_schema.AdminJwtToken) -> admin_model.AdminJwtToken:
    db_jwt = db.query(admin_model.AdminJwtToken).filter(admin_model.AdminJwtToken.admin_id == admin_id).first()
    
    db_jwt.access_token = data.access_token
    db_jwt.refresh_token = data.refresh_token
    
    db.commit()
    db.refresh(db_jwt)
    
    return db_jwt