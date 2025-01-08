from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

from db.session import get_db
from db.schemas import user_schema
from db.models import user_model
from db.crud import user_action, auth_action

from utils import utils, jwt, hash

import traceback

# OAuth2 Password Bearer
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")

router = APIRouter()

@router.post("/login", response_model=user_schema.JwtToken, status_code=status.HTTP_200_OK)
async def login_user(data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    try:
        # Check if the email is valid
        db_user = user_action.find_user_by_employee_id(db, data.username)
        if not db_user:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid username or password")

        # Check if the password is valid
        if not hash.verify_hashed_text(data.password, db_user.hashed_password):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid username or password")
                
        # Create JWT tokens
        access_token = await jwt.create_access_token("access", db_user.id)
        refresh_token = await jwt.create_refresh_token("refresh", db_user.id)
        
        # db 에 넣음
        #await user_create.create_jwt(db, db_user.id, access_token, refresh_token, "0.0.0.0")
        return user_schema.JwtToken(access_token=access_token, refresh_token=refresh_token)
    
    except Exception as e:
        db.rollback()  # transaction rollback
        print(traceback.format_exc())  # print error log on console (comment out if not needed)

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

@router.post("/refresh", response_model=user_schema.JwtToken, status_code=status.HTTP_200_OK)
async def refresh_token(refresh_token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    try:
        # Verify the refresh token
        user_id = await jwt.get_user_id_from_token(token=refresh_token)
        
        access_token = await jwt.create_access_token("access", user_id)
        return user_schema.JwtToken(access_token=access_token, refresh_token=refresh_token)
    
    except HTTPException as e:
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

@router.get("/me", response_model=user_schema.User, status_code=status.HTTP_200_OK)
async def read_user_me(access_token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    try:
        # Verify the access token
        user_id = await jwt.get_payload(token=access_token)['uid']
        db_user = user_action.find_user_by_user_id(db, user_id)
        
        if not db_user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

        return db_user
    
    except HTTPException as http_ex:
        db.rollback()

        err_msg = traceback.format_exc()
        print(err_msg)

        raise http_ex

    except SQLAlchemyError as e:
        db.rollback()

        err_msg = traceback.format_exc()
        print(err_msg)

        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")

    except Exception as e:
        db.rollback()

        err_msg = traceback.format_exc()
        print(err_msg)

        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")

    finally:
        db.close()
