from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

from core.security import user_oauth2_scheme, admin_oauth2_scheme

from db.session import get_db
from db.schemas import user_schema, experience_schema
from db.models import user_model, experience_model

from utils import utils, jwt, hash

import traceback

router = APIRouter()

# 본인의 경험치 조회
@router.get("/experiences", status_code=status.HTTP_200_OK)
async def get_experiences(access_token: str = Depends(user_oauth2_scheme), db: Session = Depends(get_db)):
    try:
        uid = jwt.admin_decode_access_token(db, access_token).get("uid")

        db_experiences = experience_action.get_experiences(db, uid)
        if not db_experiences:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Experiences not found"
            )
        
        return db_experiences
    
    except Exception as e:
        print(traceback.format_exc())
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )
    finally:
        db.close()

# 어드민만 사용 가능한 API (경험치 부여)
@router.post("/experiences", status_code=status.HTTP_201_CREATED)
async def create_experience(data: experience_schema.ExperienceCreate, access_token: str = Depends(admin_oauth2_scheme), db: Session = Depends(get_db)):
    try:
        uid = jwt.admin_decode_access_token(db, access_token).get("uid")

        db_experiences = await experience_action.create_experience(db, uid, data.amount, data.created_at)
        if not db_experiences:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to create experience")

        return {"detail": "Experience created successfully"}

    except Exception as e:
        db.rollback()
        print(traceback.format_exc())
        
        # Check the exception type
        if isinstance(e, HTTPException):
            raise e
        elif isinstance(e, SQLAlchemyError):
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Database error occurred"
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Internal server error"
            )
    finally:
        db.close()


# 레벨 조건 조회
@router.get("/levels", status_code=status.HTTP_200_OK)
async def get_levels(
    db: Session = Depends(get_db)
):
    try:
        db_levels = utils.get_levels(db)
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