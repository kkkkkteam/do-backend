from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

from db.session import get_db
from db.schemas import user_schema
from db.models import user_model
from db.crud import user_action

from utils import utils, jwt, hash

import traceback

router = APIRouter()

@router.post("/users", status_code=status.HTTP_201_CREATED)
async def create_user(data: user_schema.UserCreate, db: Session = Depends(get_db)):
    try:
        # Check if the user already exists
        db_user = user_action.find_user_by_employee_id(db, data.employee_id)
        if db_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="The user with this employee_id already exists in the system"
            )
        
        # Create a new user
        db_user = await user_action.create_user(db, data)
        
        return {"detail": "User created successfully"}
    
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