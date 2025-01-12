from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy import and_, or_
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from datetime import datetime, timedelta, timezone

from core.security import user_oauth2_scheme, admin_oauth2_scheme
from core.etc import KST

from db.session import get_db
from db.schemas import user_schema, experience_schema
from db.models import user_model, experience_model

from utils import utils, jwt, hash

import traceback

router = APIRouter()

# Only can be accessed by the admin or the leader
@router.post("", status_code=status.HTTP_201_CREATED)
async def create_experience(
    data: experience_schema.ExperienceCreate,
    access_token: str = Depends(admin_oauth2_scheme),
    db: Session = Depends(get_db)
):
    try:
        uid = jwt.admin_leader_decode_access_token(db, access_token).get("uid")
        
        if data.amount <= 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="The amount must be greater than 0"
            )
        
        # Check if the employee exists
        db_user = db.query(user_model.User).filter(user_model.User.employee_id == data.employee_id).first()
        if not db_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="The employee with this ID does not exist in the system"
            )

        # Create experience
        db_experience = experience_model.Experience(
            user_id=db_user.id,
            amount=data.amount
        )
        db.add(db_experience)
        db.commit()
        db.refresh(db_experience)
        if not db_experience:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to create experience")

        # Return success message
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




