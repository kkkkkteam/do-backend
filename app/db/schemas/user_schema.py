from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class UserBase(BaseModel):
    employee_id: str
    username: str
    name: str
    level: int
    join_date: datetime
    department: str

class UserCreate(UserBase):
    password: str

class JwtToken(BaseModel):
    access_token: str
    refresh_token: str