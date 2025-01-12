from fastapi import APIRouter, Depends, HTTPException, status, Query
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy import and_
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

from core.security import user_oauth2_scheme, admin_oauth2_scheme

from db.session import get_db
from db.schemas import admin_schema, user_schema
from db.models import admin_model, user_model
from db.crud import admin_action, user_action

from utils import utils, jwt, hash

import traceback

router = APIRouter()

@router.get("/users", response_model=user_schema.Users, status_code=status.HTTP_200_OK)
async def get_users(
    access_token: str = Depends(admin_oauth2_scheme),
    db: Session = Depends(get_db),
    skip: int = Query(0, ge=0),  # 기본값: 0, 0 이상의 값만 허용
    limit: int = Query(10, gt=0)   # 기본값: 10, 0보다 큰 값만 허용
):
    try:
        user_id = jwt.admin_decode_access_token(db, access_token).get("uid")

        # 데이터베이스에서 페이지네이션으로 사용자 가져오기
        db_users = user_action.find_users_with_pagination(db, skip=skip, limit=limit)
        if not db_users:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Users not found"
            )
        
        # 사용자 정보 가공
        users = []
        for user in db_users:
            department_name = user_action.find_department_by_department_id(db, user.department_id).name
            job_group_name = user_action.find_job_group_by_job_group_id(db, user.job_group_id).name
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

        return user_schema.Users(data=users)

    except Exception as e:
        print(traceback.format_exc())
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )
    finally:
        db.close()

@router.get("/user/{employee_id}", response_model=user_schema.UserBase, status_code=status.HTTP_200_OK)
async def get_user(
    employee_id: str,
    access_token: str = Depends(admin_oauth2_scheme),
    db: Session = Depends(get_db)
):
    try:
        user_id = jwt.admin_decode_access_token(db, access_token).get("uid")

        db_user = user_action.find_user_by_employee_id(db, employee_id)
        if not db_user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        department_name = user_action.find_department_by_department_id(db, db_user.department_id).name
        job_group_name = user_action.find_job_group_by_job_group_id(db, db_user.job_group_id).name
        if not department_name or not job_group_name:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Department or Job group not found"
            )
        
        user_base = user_schema.UserBase(
            employee_id=db_user.employee_id,
            username=db_user.username,
            name=db_user.name,
            join_date=db_user.join_date,
            job_group_name=job_group_name,
            department_name=department_name
        )
        return user_base

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
        payload = jwt.admin_decode_access_token(db, access_token)

        # Check if the user already exists
        db_user = user_action.find_user_by_employee_id(db, data.employee_id)
        if db_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="The user with this employee_id already exists in the system"
            )
        
        # Create a new user
        db_user = await user_action.create_user(db, data)
        if not db_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to create user"
            )

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