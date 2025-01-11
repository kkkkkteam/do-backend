from sqlalchemy import Column, Integer, String, BigInteger, SmallInteger, ForeignKey
from sqlalchemy.orm import relationship
from db.session import Base

class Experience(Base):
    __tablename__ = "experience"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    amount = Column(BigInteger, nullable=False)  # 경험치
    year = Column(SmallInteger, nullable=False)  # 년도

    user = relationship("User", back_populates="experience")

class Level(Base):
    __tablename__ = "levels"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(20), unique=True, nullable=False)  # 예: "F1-Ⅰ"
    total_required_experience = Column(BigInteger, nullable=False)  # 총 필요 경험치

    # 사용자와의 관계 (일대다)
    users = relationship("User", back_populates="level")
