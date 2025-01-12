from fastapi import APIRouter, Depends, HTTPException, status, Query
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

from core.security import user_oauth2_scheme, admin_oauth2_scheme

from db.session import get_db
from db.schemas import admin_schema, user_schema
from db.models import admin_model, user_model
from db.crud import admin_action, user_action

from utils import utils, jwt, hash
from typing import Optional, List

import traceback

router = APIRouter()

@router.post("/department", status_code=status.HTTP_201_CREATED)
async def create_departments(
    data: user_schema.DepartmentCreate, 
    access_token: str = Depends(admin_oauth2_scheme), 
    db: Session = Depends(get_db)
):
    try:
        user_id = jwt.admin_decode_access_token(db, access_token).get("uid")

        # Check if the user already exist
        db_department = db.query(user_model.Department).filter(user_model.Department.name == data.name).first()
        if db_department:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="The department with this name already exists in the system"
            )
        
        # Add department to the database
        db_department = user_model.Department(
            name=data.name
        )
        
        db.add(db_department)
        db.commit()
        db.refresh(db_department)

        if not db_department:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to create department"
            )

        # Return success message
        return {"detail": "Department created successfully"}
    
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

@router.get("/departments", status_code=status.HTTP_200_OK)
async def get_departments(
    access_token: str = Depends(admin_oauth2_scheme), 
    db: Session = Depends(get_db)
):
    try:
        user_id = jwt.admin_decode_access_token(db, access_token).get("uid")

        db_departments = db.query(user_model.Department).all()
        if not db_departments:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Departments not found"
            )
        
        # Return departments
        return db_departments
    
    except Exception as e:
        print(traceback.format_exc())
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )
    finally:
        db.close()


