from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from datetime import datetime, timedelta, timezone

from core.security import user_oauth2_scheme, admin_oauth2_scheme

from db.session import get_db
from db.schemas import user_schema, experience_schema
from db.models import user_model, experience_model

from utils import utils, jwt, hash

import traceback

router = APIRouter()

# 레벨 조건 조회
@router.get("/levels", status_code=status.HTTP_200_OK)
async def get_levels(
    access_token: str = Depends(admin_oauth2_scheme),
    db: Session = Depends(get_db)
):
    try:
        jwt.all_decode_access_token(access_token)
        db_levels = db.query(experience_model.Level).all()
        if not db_levels:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Levels not found"
            )
        
        return db_levels
    
    except Exception as e:
        print(traceback.format_exc())
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )
    finally:
        db.close()

