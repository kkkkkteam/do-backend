from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

from core.security import user_oauth2_scheme, admin_oauth2_scheme

from db.session import get_db
from db.schemas import user_schema
from db.models import user_model

from utils import utils, jwt, hash

import traceback

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
        access_token = jwt.create_access_token("access", db_user.id)
        refresh_token = jwt.create_refresh_token("refresh", db_user.id)
        
        db_jwt = user_action.find_jwt_by_user_id(db, db_user.id)
        if db_jwt:
            user_action.update_jwt_token(db, db_user.id, user_schema.JwtToken(access_token=access_token, refresh_token=refresh_token))
        else:
            await user_action.create_jwt(db, db_user.id, user_schema.JwtToken(access_token=access_token, refresh_token=refresh_token))
        
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
async def refresh_token(refresh_token: str = Depends(user_oauth2_scheme), db: Session = Depends(get_db)):
    try:
        # Verify the refresh token
        user_id = await jwt.user_decode_access_token(db, refresh_token).get('uid')
        
        access_token = await jwt.create_access_token("access", user_id)
        if not user_action.update_jwt_token(db, user_id, user_schema.JwtToken(access_token=access_token, refresh_token=refresh_token)):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Failed to update refresh token")

        return user_schema.JwtToken(access_token=access_token, refresh_token=refresh_token)
    
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




