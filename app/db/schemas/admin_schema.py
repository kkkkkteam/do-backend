from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


class AdminCreate(BaseModel):
    username: str
    password: str

class AdminJwtToken(BaseModel):
    access_token: str
    refresh_token: str
