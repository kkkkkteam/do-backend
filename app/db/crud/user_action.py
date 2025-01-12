from sqlalchemy.orm import Session
from sqlalchemy import or_, and_, union_all

from fastapi import HTTPException
from datetime import datetime, timezone

from db.models import user_model, experience_model
from db.schemas import user_schema, admin_schema
from utils import hash

# Create
async def create_jwt(db: Session, user_id: int, data: user_schema.JwtToken) -> user_model.UserJwtToken:
    db_jwt = user_model.UserJwtToken(
        user_id=user_id,
        access_token=data.access_token,
        refresh_token=data.refresh_token
    )
    
    db.add(db_jwt)
    db.commit()
    db.refresh(db_jwt)
    
    return db_jwt

async def create_user(db: Session, data: user_schema.UserCreate) -> user_model.User:
    
    hashed_password = hash.hash_text(data.password)

    db_department = find_department_by_department_name(db, data.department_name)
    if not db_department:
        raise HTTPException(status_code=404, detail="Department not found")

    db_job_group = find_job_group_by_job_group_name(db, data.job_group_name)
    if not db_job_group:
        raise HTTPException(status_code=404, detail="Job group not found")
    
    db_user = user_model.User(
        employee_id=data.employee_id,
        username=data.username,
        hashed_password=hashed_password,
        name=data.name,
        join_date=data.join_date,
        department_id=db_department.id,
        job_group_id=db_job_group.id
    )
    
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    return db_user

async def create_department(db: Session, name: str) -> user_model.Department:
    db_department = user_model.Department(
        name=name
    )
    
    db.add(db_department)
    db.commit()
    db.refresh(db_department)
    
    return db_department

async def create_job_group(db: Session, name: str) -> user_model.JobGroup:
    db_job_group = user_model.JobGroup(
        name=name
    )
    
    db.add(db_job_group)
    db.commit()
    db.refresh(db_job_group)
    
    return db_job_group

# Read
def find_user_by_employee_id(db: Session, employee_id: str) -> user_model.User:
    return db.query(user_model.User).filter(user_model.User.employee_id == employee_id).first()

def find_user_by_user_id(db: Session, user_id: int) -> user_model.User:
    return db.query(user_model.User).filter(user_model.User.id == user_id).first()

def find_jwt_by_user_id(db: Session, user_id: int) -> user_model.UserJwtToken:
    return db.query(user_model.UserJwtToken).filter(user_model.UserJwtToken.user_id == user_id).first()

def find_department_by_department_name(db: Session, department_name: str) -> user_model.Department:
    return db.query(user_model.Department).filter(user_model.Department.name == department_name).first()

def find_department_by_department_id(db: Session, department_id: int) -> user_model.Department:
    return db.query(user_model.Department).filter(user_model.Department.id == department_id).first()

def find_job_group_by_job_group_name(db: Session, job_group_name: str) -> user_model.JobGroup:
    return db.query(user_model.JobGroup).filter(user_model.JobGroup.name == job_group_name).first()

def find_job_group_by_job_group_id(db: Session, job_group_id: int) -> user_model.JobGroup:
    return db.query(user_model.JobGroup).filter(user_model.JobGroup.id == job_group_id).first()

def find_departments_all(db: Session) -> list[user_model.Department]:
    return db.query(user_model.Department).all()

def find_job_groups_all(db: Session) -> list[user_model.JobGroup]:
    return db.query(user_model.JobGroup).all()

def find_users_all(db: Session) -> list[user_model.User]:
    return db.query(user_model.User).all()

def find_users_with_pagination(db: Session, skip: int, limit: int) -> list[user_model.User]:
    return db.query(user_model.User).offset(skip).limit(limit).all()

# Update
async def update_jwt_token(db: Session, user_id: int, data: user_schema.JwtToken) -> user_model.UserJwtToken:
    db_jwt = db.query(user_model.UserJwtToken).filter(user_model.UserJwtToken.user_id == user_id).first()
    
    db_jwt.access_token = data.access_token
    db_jwt.refresh_token = data.refresh_token
    
    db.commit()
    db.refresh(db_jwt)

    return db_jwt

# Delete
