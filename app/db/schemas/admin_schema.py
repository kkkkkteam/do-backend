from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class AdminBase(BaseModel):
    username: str
    created_at: Optional[datetime]

class AdminCreate(AdminBase):
    password: str

class AdminJwtToken(BaseModel):
    access_token: str
    refresh_token: str

class DepartmentBase(BaseModel):
    name: str

class DepartmentCreate(DepartmentBase):
    pass