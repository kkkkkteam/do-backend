from fastapi import APIRouter, Depends, HTTPException, status, Query
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from datetime import datetime, timezone

from core.security import user_oauth2_scheme, admin_oauth2_scheme
from core.etc import KST

from db.session import get_db
from db.schemas import admin_schema, user_schema
from db.models import admin_model, user_model

from utils import utils, jwt, hash

import traceback

router = APIRouter()

@router.post("", response_model=admin_schema.AdminJwtToken, status_code=status.HTTP_201_CREATED)
async def create_admin(
    data: admin_schema.AdminCreate, 
    db: Session = Depends(get_db)
):
    try:
        # Check if the user already exists
        db_admin = db.query(admin_model.Admin).filter(admin_model.Admin.username == data.username).first()
        if db_admin:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="The user with this username already exists in the system"
            )
        
        # Add user to the database
        hashed_password = hash.hash_text(data.password)

        db_admin = admin_model.Admin(
            username=data.username,
            hashed_password=hashed_password,
            created_at=datetime.now(KST)
        )
        
        db.add(db_admin)
        db.commit()
        db.refresh(db_admin)
        
        if not db_admin:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to create admin"
            )
        
        # Create JWT token
        access_token = jwt.create_access_token("access", db_admin.id, jwt.Permission.ADMIN)
        refresh_token = jwt.create_refresh_token("refresh", db_admin.id, jwt.Permission.ADMIN)

        # Add JWT token to the database
        db_admin_jwt = admin_model.AdminJwtToken(
            admin_id=db_admin.id,
            access_token=access_token,
            refresh_token=refresh_token
        )
        
        db.add(db_admin_jwt)
        db.commit()
        db.refresh(db_admin_jwt)
        
        if not db_admin_jwt:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to create admin jwt"
            )
        
        # Return JWT token(access, refresh)
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



