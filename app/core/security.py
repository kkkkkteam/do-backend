from fastapi.security import OAuth2PasswordBearer
from fastapi import FastAPI, Depends, HTTPException, Security
from fastapi.openapi.utils import get_openapi

app = FastAPI()

admin_oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/admin/login")
user_oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/user/login")