from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class UserBase(BaseModel):
    employee_id: str
    username: str
    name: str
    join_date: datetime
    job_group_name: str
    department_name: str

class Users(BaseModel):
    data: List[UserBase]

class UserCreate(UserBase):
    password: str

class JwtToken(BaseModel):
    access_token: str
    refresh_token: str

class DepartmentBase(BaseModel):
    name: str

class DepartmentCreate(DepartmentBase):
    pass

class JobGroupBase(BaseModel):
    name: str

class JobGroupCreate(JobGroupBase):
    pass

class Departments(BaseModel):
    data: List[DepartmentBase]

class JobGroups(BaseModel):
    data: List[JobGroupBase]