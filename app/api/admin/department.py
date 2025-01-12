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

import traceback

router = APIRouter()

@router.post("/departments", status_code=status.HTTP_201_CREATED)
async def create_departments(
    data: user_schema.DepartmentCreate, 
    access_token: str = Depends(admin_oauth2_scheme), 
    db: Session = Depends(get_db)
):
    try:
        user_id = jwt.admin_decode_access_token(db, access_token).get("uid")

        db_department = user_action.find_department_by_department_name(db, data.name)
        if db_department:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="The department with this name already exists in the system"
            )
        
        db_department = await user_action.create_department(db, data.name)

        if not db_department:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to create department"
            )

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

@router.get("/departments", response_model=user_schema.Departments, status_code=status.HTTP_200_OK)
async def get_departments(
    access_token: str = Depends(admin_oauth2_scheme), 
    db: Session = Depends(get_db)
):
    try:
        user_id = jwt.admin_decode_access_token(db, access_token).get("uid")

        db_departments = user_action.find_departments_all(db)
        if not db_departments:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Departments not found"
            )
        # db_departments 를 Departments 로 반환하도록 하세요
        departments = [user_schema.DepartmentBase(name=dept.name) for dept in db_departments]
        return user_schema.Departments(data=departments)
    
    except Exception as e:
        print(traceback.format_exc())
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )
    finally:
        db.close()


