from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy import and_, or_
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from datetime import datetime, timedelta, timezone

from core.security import user_oauth2_scheme, admin_oauth2_scheme
from core.etc import Permission, KST

from db.session import get_db
from db.schemas import user_schema
from db.models import user_model

from utils import utils, jwt, hash

import traceback

router = APIRouter()

@router.post("/login", response_model=user_schema.JwtToken, status_code=status.HTTP_200_OK)
async def login_user(
    data: OAuth2PasswordRequestForm = Depends(), 
    db: Session = Depends(get_db)
):
    try:
        # Check if the email is valid
        db_user = db.query(user_model.User).filter(or_(
            user_model.User.username == data.username, user_model.User.employee_id == data.username)).first()
        if not db_user:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid username or password")

        # Check if the password is valid
        if not hash.verify_hashed_text(data.password, db_user.hashed_password):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid username or password")
        
        # Create JWT tokens
        if db_user.permission_type == Permission.LEADER:
            access_token = jwt.create_access_token("access", db_user.id, Permission.LEADER)
            refresh_token = jwt.create_refresh_token("refresh", db_user.id, Permission.LEADER)
        else:
            access_token = jwt.create_access_token("access", db_user.id, Permission.USER)
            refresh_token = jwt.create_refresh_token("refresh", db_user.id, Permission.USER)
        
        db_jwt = db.query(user_model.UserJwtToken).filter(user_model.UserJwtToken.user_id == db_user.id).first()
        if db_jwt:
            # Update JWT token in the database
            db_jwt.access_token = access_token
            db_jwt.refresh_token = refresh_token
            db.commit()
            db.refresh(db_jwt)
        else:
            # Add JWT token to the database
            db_jwt = user_model.UserJwtToken(
                user_id=db_user.id,
                access_token=access_token,
                refresh_token=refresh_token
            )
            db.add(db_jwt)
            db.commit()
            db.refresh(db_jwt)
            if not db_jwt:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Failed to create JWT token"
                )
        
        # Return JWT token
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
async def refresh_token(
    refresh_token: str = Depends(user_oauth2_scheme), 
    db: Session = Depends(get_db)
):
    try:
        # Verify the refresh token
        user_id = jwt.user_decode_refresh_token(db, refresh_token).get('uid')
        
        access_token = jwt.create_access_token("access", user_id)
        
        # Update JWT token in the database
        db_jwt = db.query(user_model.UserJwtToken).filter(user_model.UserJwtToken.user_id == user_id).first()
        if db_jwt:
            db_jwt.access_token = access_token
            db.commit()
            db.refresh(db_jwt)
        else:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Failed to update refresh token")

        # Return JWT token
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



