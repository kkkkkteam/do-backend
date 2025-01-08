from sqlalchemy.orm import Session
from db.schemas import user_schema
from db.models import user_model
from db.crud.user import user_read
from sqlalchemy import and_
from fastapi import HTTPException

async def delete_token(db: Session, user_id: int):
    """jwt token을 삭제합니다"""
    db_token = user_read.find_jwt_by_userid(db, user_id)
    if db_token:
        db.delete(db_token)
        db.commit()
        return True
    
    else: 
        raise HTTPException(status_code=404, detail="Token not found")



