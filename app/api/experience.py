from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

from core.security import oauth2_scheme

from db.session import get_db
from db.schemas import user_schema
from db.models import user_model
from db.crud import user_action

from utils import utils, jwt, hash

import traceback

router = APIRouter()

@router.get("/experiences", response_model=user_schema.JwtToken, status_code=status.HTTP_200_OK)
async def get_experiences(access_token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    try:
        return user_action.get_experiences(db)
    except Exception as e:
        print(traceback.format_exc())
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )
    finally:
        db.close()


