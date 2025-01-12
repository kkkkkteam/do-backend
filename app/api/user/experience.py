from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy import and_, or_
from sqlalchemy.orm import Session, joinedload
from sqlalchemy.exc import SQLAlchemyError
from datetime import datetime, timedelta, timezone

from core.security import user_oauth2_scheme, admin_oauth2_scheme

from db.session import get_db
from db.schemas import user_schema, experience_schema
from db.models import user_model, experience_model

from utils import utils, jwt, hash

import traceback

router = APIRouter()

# 본인의 경험치 조회
@router.get("", response_model=experience_schema.Experiences, status_code=status.HTTP_200_OK)
async def get_experiences(access_token: str = Depends(user_oauth2_scheme), db: Session = Depends(get_db)):
    try:
        uid = jwt.user_leader_decode_access_token(db, access_token).get("uid")

        db_user = db.query(user_model.User).options(joinedload(user_model.User.experiences)).filter(user_model.User.id == uid).first()

        if not db_user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Experiences not found"
            )
        
        total_exp = sum(db_exp.amount for db_exp in db_user.experiences)
        
        return experience_schema.Experiences(total_experience=total_exp, data=db_user.experiences)
    
    except Exception as e:
        print(traceback.format_exc())
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )
    finally:
        db.close()
