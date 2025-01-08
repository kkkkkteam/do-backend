from sqlalchemy.orm import Session
from sqlalchemy import or_, and_, union_all

from fastapi import HTTPException
from datetime import datetime, timezone

from db.models import user_model
from db.schemas import user_schema, auth_schema
from utils.jwt import Permission