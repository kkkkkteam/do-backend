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


