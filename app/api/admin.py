from fastapi import APIRouter, Depends, HTTPException, status
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

@router.post("/login")
async def login_admin(data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    try:
        # Check if the username is valid
        db_admin = admin_action.find_admin_by_username(db, data.username)
        if not db_admin:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid username or password")

        # Check if the password is valid
        if not hash.verify_hashed_text(data.password, db_admin.hashed_password):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid username or password")
        
        access_token = jwt.create_access_token("access", db_admin.id, jwt.Permission.ADMIN)
        refresh_token = jwt.create_refresh_token("refresh", db_admin.id, jwt.Permission.ADMIN)
        
        db_admin_jwt = admin_action.find_admin_jwt_by_admin_id(db, db_admin.id)
        if db_admin_jwt:
            await admin_action.update_admin_jwt_token(db, db_admin.id, admin_schema.AdminJwtToken(access_token=access_token, refresh_token=refresh_token))
        else:
            await admin_action.create_admin_jwt(db, db_admin.id, admin_schema.AdminJwtToken(access_token=access_token, refresh_token=refresh_token))
        
        return admin_schema.AdminJwtToken(access_token=access_token, refresh_token=refresh_token)

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

@router.post("", response_model=admin_schema.AdminJwtToken, status_code=status.HTTP_201_CREATED)
async def create_admin(data: admin_schema.AdminCreate, db: Session = Depends(get_db)):
    try:
        # Check if the user already exists
        db_admin = admin_action.find_admin_by_username(db, data.username)
        if db_admin:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="The user with this employee_id already exists in the system"
            )
        
        # Create a new user
        db_admin = await admin_action.create_admin(db, data)
        if not db_admin:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to create admin"
            )
        
        access_token = jwt.create_access_token("access", db_admin.id, jwt.Permission.ADMIN)
        refresh_token = jwt.create_refresh_token("refresh", db_admin.id, jwt.Permission.ADMIN)

        db_admin_jwt = await admin_action.create_admin_jwt(db, db_admin.id, 
                    admin_schema.AdminJwtToken(access_token=access_token, refresh_token=refresh_token))
        
        if not db_admin_jwt:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to create admin jwt"
            )
        
        return admin_schema.AdminJwtToken(access_token=access_token, refresh_token=refresh_token)
    
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

@router.post("/users", status_code=status.HTTP_201_CREATED)
async def create_user(data: user_schema.UserCreate, access_token: str = Depends(admin_oauth2_scheme),  db: Session = Depends(get_db)):
    try:
        payload = jwt.admin_decode_access_token(db, access_token)

        # Check if the user already exists
        db_user = user_action.find_user_by_employee_id(db, data.employee_id)
        if db_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="The user with this employee_id already exists in the system"
            )
        
        # Create a new user
        db_user = await user_action.create_user(db, data)
        if not db_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to create user"
            )

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

@router.post("/departments")
async def create_departments(data: admin_schema.DepartmentCreate, access_token: str = Depends(admin_oauth2_scheme), db: Session = Depends(get_db)):
    try:
        payload = jwt.admin_decode_access_token(db, access_token)

        db_department = user_action.find_department_by_department_name(db, data.name)
        if db_department:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="The department with this name already exists in the system"
            )
        
        db_department = user_action.create_department(db, data)

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

