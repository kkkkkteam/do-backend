from sqlalchemy import Boolean, Column, Integer, String, ForeignKey, BigInteger, SmallInteger, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import ENUM

from datetime import datetime, timezone

from core.etc import KST, Permission

from db.session import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    employee_id = Column(String(100), unique=True, index=True, nullable=False) # 사원 번호(사번)
    username = Column(String(50), unique=True, index=True, nullable=False) # 사용자 아이디
    hashed_password = Column(String(255), nullable=False) # 비밀번호
    name = Column(String(50), nullable=False) # 이름
    join_date = Column(DateTime, default=datetime.now(KST), nullable=False) # 입사일
    permission_type = Column(ENUM(Permission), default=Permission.USER, nullable=False) # 권한

    job_group_id = Column(Integer, ForeignKey("job_group.id"), nullable=False) # 직무 그룹
    department_id = Column(Integer, ForeignKey("departments.id"), nullable=False) # 부서

    profile_url = relationship("UserProfile", back_populates="user")
    token = relationship("UserJwtToken", back_populates="user")
    
    experience = relationship("Experience", back_populates="user")

    job_group = relationship("JobGroup", back_populates="user")
    department = relationship("Department", back_populates="user")

class Department(Base):
    __tablename__ = "departments"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(50), unique=True, index=True, nullable=False)
    is_active = Column(Boolean, default=True)

    user = relationship("User", back_populates="department")


class JobGroup(Base):
    __tablename__ = "job_group"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(50), unique=True, index=True, nullable=False)
    is_active = Column(Boolean, default=True)

    user = relationship("User", back_populates="job_group")

class UserProfile(Base):
    __tablename__ = "user_profile"

    user_id = Column(Integer, ForeignKey("users.id"), primary_key=True)
    profile_url = Column(String(255), nullable=False) # 캐릭터 이미지 URL (캐릭터)
    banner_url = Column(String(255), nullable=False) # 배너 이미지 URL (배경)

    user = relationship("User", back_populates="profile_url")

class UserJwtToken(Base):
    __tablename__ = "user_jwt_tokens"
    
    user_id = Column(Integer, ForeignKey("users.id"), primary_key=True)
    access_token = Column(String(255), nullable=False, index=True)
    refresh_token = Column(String(255), nullable=False)

    user = relationship("User", back_populates="token")



