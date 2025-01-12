from fastapi import APIRouter, Depends, HTTPException, status, Query
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

from core.security import user_oauth2_scheme, admin_oauth2_scheme

from db.session import get_db
from db.schemas import admin_schema, user_schema
from db.models import admin_model, user_model

from utils import utils, jwt, hash

import traceback

router = APIRouter()

@router.post("/job_group", status_code=status.HTTP_201_CREATED)
async def create_job_groups(
    data: user_schema.JobGroupCreate, 
    access_token: str = Depends(admin_oauth2_scheme), 
    db: Session = Depends(get_db)
):
    try:
        user_id = jwt.admin_decode_access_token(db, access_token).get("uid")

        # Check if the job group already exist
        db_job_group = db.query(user_model.JobGroup).filter(user_model.JobGroup.name == data.name).first()
        if db_job_group:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="The job group with this name already exists in the system"
            )
        
        # Add job group to the database
        db_job_group = user_model.JobGroup(
            name=data.name
        )
        
        db.add(db_job_group)
        db.commit()
        db.refresh(db_job_group)

        if not db_job_group:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to create job group"
            )

        # Return success message
        return {"detail": "Job group created successfully"}
    
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

@router.get("/job_groups", status_code=status.HTTP_200_OK)
async def get_job_groups_all(
    access_token: str = Depends(admin_oauth2_scheme), 
    db: Session = Depends(get_db)
):
    try:
        user_id = jwt.admin_decode_access_token(db, access_token).get("uid")

        # Get job groups from the database
        db_job_groups = db.query(user_model.JobGroup).all()
        if not db_job_groups:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Job groups not found"
            )
        
        # Return job groups
        return db_job_groups
    
    except Exception as e:
        print(traceback.format_exc())
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )
    finally:
        db.close()


