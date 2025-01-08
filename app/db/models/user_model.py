from db.session import Base
from sqlalchemy import Boolean, Column, Integer, String, ForeignKey, BigInteger, SmallInteger, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import ENUM

from datetime import datetime, timezone

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    employee_id = Column(String(100), unique=True, index=True, nullable=False) # 사원 번호(사번)
    username = Column(String(50), unique=True, index=True, nullable=False) # 사용자 아이디
    hashed_password = Column(String(255), nullable=False) # 비밀번호
    name = Column(String(50), nullable=False) # 이름
    level = Column(BigInteger, nullable=False) # 레벨
    join_date = Column(DateTime, nullable=False) # 입사일
    department = Column(String(50), nullable=False) # 부서(소속)

    experience = relationship("Experience", back_populates="user")
    profile_url = relationship("UserProfile", back_populates="user")
    token = relationship("JwtToken", back_populates="user")

class Experience(Base):
    __tablename__ = "experience"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    amount = Column(BigInteger, nullable=False) # 경험치
    year = Column(SmallInteger, nullable=False) # 년도

    user = relationship("User", back_populates="experience")

class UserProfile(Base):
    __tablename__ = "user_profile"

    user_id = Column(Integer, ForeignKey("users.id"), primary_key=True)
    profile_url = Column(String(255), nullable=False) # 캐릭터 이미지 URL (캐릭터)
    banner_url = Column(String(255), nullable=False) # 배너 이미지 URL (배경)

    user = relationship("User", back_populates="profile_url")

class JwtToken(Base):
    __tablename__ = "jwt_tokens"
    
    user_id = Column(Integer, ForeignKey("users.id"), primary_key=True)
    access_token = Column(String(255), nullable=False, index=True)
    refresh_token = Column(String(255), nullable=False)

    user = relationship("User", back_populates="token")