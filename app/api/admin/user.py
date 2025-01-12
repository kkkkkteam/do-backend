from fastapi import APIRouter, Depends, HTTPException, status, Query
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy import and_
from sqlalchemy.orm import Session, joinedload
from sqlalchemy.exc import SQLAlchemyError

from core.security import user_oauth2_scheme, admin_oauth2_scheme
from core.etc import KST, Permission

from db.session import get_db
from db.schemas import admin_schema, user_schema
from db.models import admin_model, user_model, experience_model
from db.crud import admin_action, user_action

from utils import utils, jwt, hash

import traceback

router = APIRouter()

@router.get("/users", status_code=status.HTTP_200_OK)
async def get_users(
    access_token: str = Depends(admin_oauth2_scheme),
    db: Session = Depends(get_db),
    skip: int = Query(0, ge=0),  # 기본값: 0, 0 이상의 값만 허용
    limit: int = Query(10, gt=0)   # 기본값: 10, 0보다 큰 값만 허용
):
    try:
        user_id = jwt.admin_decode_access_token(db, access_token).get("uid")

        # Get users from the database with pagination
        db_users = db.query(user_model.User).offset(skip).limit(limit).all()
        if not db_users:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Users not found"
            )
        
        # Data processing
        users = []
        for user in db_users:
            department_name = db.query(user_model.Department).filter(user_model.Department.id == user.department_id).first().name
            job_group_name = db.query(user_model.JobGroup).filter(user_model.JobGroup.id == user.job_group_id).first().name
            if not department_name or not job_group_name:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Department or Job group not found"
                )
            user_base = user_schema.UserBase(
                employee_id=user.employee_id,
                username=user.username,
                name=user.name,
                join_date=user.join_date,
                job_group_name=job_group_name,
                department_name=department_name
            )
            users.append(user_base)

        return users
    except Exception as e:
        print(traceback.format_exc())
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )
    finally:
        db.close()

@router.get("/user/{employee_id}", status_code=status.HTTP_200_OK)
async def get_user(
    employee_id: str,
    access_token: str = Depends(admin_oauth2_scheme),
    db: Session = Depends(get_db)
):
    try:
        user_id = jwt.admin_decode_access_token(db, access_token).get("uid")

        db_user = (
            db.query(user_model.User)
            .options(
                joinedload(user_model.User.job_group),
                joinedload(user_model.User.department),
                joinedload(user_model.User.experience)
            )
            .filter(user_model.User.employee_id == employee_id)
            .first()
        )
        
        if not db_user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

        if not db_user.job_group or not db_user.department:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Job group or Department not found"
            )
        
        # Caclulate total experience
        total_exp = sum(db_exp.amount for db_exp in db_user.experience)
        
        # Find the level corresponding to the total_exp
        db_level = (
            db.query(experience_model.Level)
            .filter(experience_model.Level.total_required_experience <= total_exp)
            .order_by(experience_model.Level.total_required_experience.desc())
            .first()
        )

        # If a matching level is found, get its name
        level_name = db_level.name if db_level else "No Level"
        
        # Return user
        return user_schema.UserBase(
            employee_id=db_user.employee_id,
            username=db_user.username,
            name=db_user.name,
            join_date=db_user.join_date,
            job_group_name=db_user.job_group.name,
            department_name=db_user.department.name,
            total_experience=total_exp,
            level=level_name
        )

    except Exception as e:
        print(traceback.format_exc())
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )
    finally:
        db.close()

@router.post("/user", status_code=status.HTTP_201_CREATED)
async def create_user(
    data: user_schema.UserCreate, 
    access_token: str = Depends(admin_oauth2_scheme), 
    db: Session = Depends(get_db)
):
    try:
        user_id = jwt.admin_decode_access_token(db, access_token).get("uid")

        # Check if the user already exists
        db_user = db.query(user_model.User).filter(user_model.User.employee_id == data.employee_id).first()
        if db_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="The user with this employee_id already exists in the system"
            )
        
        # Check if the department and job group exist
        db_department, db_job_group = (
            db.query(user_model.Department, user_model.JobGroup)
            .filter(user_model.Department.name == data.department_name)
            .filter(user_model.JobGroup.name == data.job_group_name)
            .first()
        )

        if not db_department or not db_job_group:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Department or Job group not found"
            )
        
        # Check permission
        perm = Permission.USER.value
        if data.permission.lower() == "leader":
            perm = Permission.LEADER.value
        else:
            perm = Permission.USER.value
        
        # Create a new user
        db_user = user_model.User(
            employee_id=data.employee_id,
            username=data.username,
            name=data.name,
            join_date=data.join_date,
            department_id=data.db_department.id,
            job_group_id=data.db_job_group.id,
            permission_type=perm
        )
        
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        
        if not db_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to create user"
            )

        # Return success message
        return {"detail": "User created successfully"}
    
    except Exception as e:
        db.rollback()
        print(traceback.format_exc())
        
        # Check the exception type
        if isinstance(e, HTTPException):
            raise e
        elif isinstance(e, SQLAlchemyError):
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Database error occurred"
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Internal server error"
            )
    finally:
        db.close()

@router.post("user/{employee_id}/favorite", status_code=status.HTTP_201_CREATED)
async def add_user_favorite(
    employee_id: str,
    access_token: str = Depends(user_oauth2_scheme),
    db: Session = Depends(get_db)
):
    try:
        uid = jwt.user_decode_access_token(db, access_token).get("uid")
        
        # Check if the user exists
        db_user = db.query(user_model.User).filter(user_model.User.employee_id == employee_id).first()
        if not db_user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Check if the user is already in the favorite list
        db_favorite = db.query(admin_model.Favorite).filter(and_(
            admin_model.Favorite.employee_id == employee_id,admin_model.Favorite.admin_id == uid)).first()
        
        if db_favorite:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="The user is already in the favorite list"
            )
        
        # Add favorite
        db_favorite = admin_model.Favorite(employee_id=employee_id, admin_id=uid)
        db.add(db_favorite)
        db.commit()
        db.refresh(db_favorite)
        
        if not db_favorite:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to add favorite"
            )

        return {"detail": "Favorite added successfully"}

    except Exception as e:
        db.rollback()
        print(traceback.format_exc())
        
        # Check the exception type
        if isinstance(e, HTTPException):
            raise e
        elif isinstance(e, SQLAlchemyError):
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Database error occurred"
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Internal server error"
            )
    finally:
        db.close()