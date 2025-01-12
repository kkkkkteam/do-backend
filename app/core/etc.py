from fastapi import FastAPI, Depends, HTTPException, Security
from fastapi.security import OAuth2PasswordBearer
from fastapi.openapi.utils import get_openapi

from datetime import datetime, timedelta, timezone

from enum import Enum

app = FastAPI()

# KST = 한국 서울표준시
KST = timezone(timedelta(hours=9), "KST")

class Permission(Enum):
    ADMIN = "*"
    LEADER = "+"
    USER = "-"
