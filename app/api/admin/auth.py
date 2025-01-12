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

@router.post("/login", response_model=admin_schema.AdminJwtToken, status_code=status.HTTP_200_OK)
async def login_admin(
    data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    try:
        # Check if the username is valid
        db_admin = db.query(admin_model.Admin).filter(admin_model.Admin.username == data.username).first()
        if not db_admin:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid username or password")

        # Check if the password is valid
        if not hash.verify_hashed_text(data.password, db_admin.hashed_password):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid username or password")
        
        # Create JWT token
        access_token = jwt.create_access_token("access", db_admin.id, jwt.Permission.ADMIN)
        refresh_token = jwt.create_refresh_token("refresh", db_admin.id, jwt.Permission.ADMIN)
        
        # Sync JWT token with the database
        db_admin_jwt = db.query(admin_model.AdminJwtToken).filter(admin_model.AdminJwtToken.admin_id == db_admin.id).first()
        if db_admin_jwt:
            # Update JWT token in the database
            db_admin_jwt.access_token = data.access_token
            db_admin_jwt.refresh_token = data.refresh_token
            
            db.commit()
            db.refresh(db_admin_jwt)
        else:
            # Add JWT token to the database
            db_admin_jwt = admin_model.AdminJwtToken(
                admin_id=db_admin.id,
                access_token=data.access_token,
                refresh_token=data.refresh_token
            )
            
            db.add(db_admin_jwt)
            db.commit()
            db.refresh(db_admin_jwt)
        
        # Return JWT token
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




