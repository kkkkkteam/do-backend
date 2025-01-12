from sqlalchemy import Column, Integer, String, BigInteger, SmallInteger, ForeignKey, DateTime
from sqlalchemy.orm import relationship

from datetime import datetime, timezone

from core.etc import KST
from db.session import Base

class Experience(Base):
    __tablename__ = "experience"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    amount = Column(BigInteger, nullable=False)  # 경험치
    created_at = Column(DateTime, default=datetime.now(KST), nullable=False)  # 경험치를 받은 날짜

    user = relationship("User", back_populates="experience")

class Level(Base):
    __tablename__ = "levels"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(20), unique=True, nullable=False)  # 예: "F1-Ⅰ"
    total_required_experience = Column(BigInteger, nullable=False)  # 총 필요 경험치
