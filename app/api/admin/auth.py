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




