from sqlalchemy import Boolean, Column, Integer, String, ForeignKey, BigInteger, SmallInteger, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import ENUM

from datetime import datetime, timezone

from core.etc import KST
from db.session import Base

class Admin(Base):
    __tablename__ = "admins"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    username = Column(String(50), unique=True, index=True, nullable=False) # 사용자 아이디
    hashed_password = Column(String(255), nullable=False) # 비밀번호

    created_at = Column(DateTime, default=datetime.now(KST), nullable=False) # 가입일

    favorites = relationship("Favorite", back_populates="admin")
    token = relationship("AdminJwtToken", back_populates="admin")

class AdminJwtToken(Base):
    __tablename__ = "admin_jwt_tokens"
    
    admin_id = Column(Integer, ForeignKey("admins.id"), primary_key=True)
    access_token = Column(String(255), nullable=False, index=True)
    refresh_token = Column(String(255), nullable=False)

    admin = relationship("Admin", back_populates="token")

class Favorite(Base):
    __tablename__ = "favorites"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    admin_id = Column(Integer, ForeignKey("admins.id"), nullable=False)

    admin = relationship("Admin", back_populates="favorites")
