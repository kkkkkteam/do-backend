from sqlalchemy.orm import Session
from sqlalchemy import or_, and_, union_all

from fastapi import HTTPException
from datetime import datetime, timezone

from db.schemas import experience_schema
from db.models import experience_model


async def create_experience(db: Session, user_id: int, amount: int, created_at: datetime) -> experience_model.Experience:
    db_experience = experience_model.Experience(
        user_id=user_id,
        amount=amount,
        created_at=created_at
    )
    
    db.add(db_experience)
    db.commit()
    db.refresh(db_experience)
    
    return db_experience

def get_experiences(db: Session, user_id: int) -> list[experience_schema.Experiences]:
    return db.query(experience_model.Experience).filter(experience_model.Experience.user_id == user_id).all()

