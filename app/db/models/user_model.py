from db.session import Base
from sqlalchemy import Boolean, Column, Integer, String, ForeignKey, BigInteger, SmallInteger, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import ENUM

from datetime import datetime, timezone


# 사용자 테이블
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    employee_id = Column(String(100), unique=True, nullable=False)  # 사번
    name = Column(String(50), nullable=False)  # 이름
    department = Column(String(50), nullable=False)  # 소속
    job_group = Column(String(50), nullable=False)  # 직무 그룹
    level = Column(String(50), nullable=False)  # 레벨

    yearly_experience = relationship("YearlyExperience", back_populates="user")
    performance_evaluations = relationship("PerformanceEvaluation", back_populates="user")
    job_quests = relationship("JobQuest", back_populates="user")
    leader_quests = relationship("LeaderQuest", back_populates="user")
    company_projects = relationship("CompanyProject", back_populates="user")

# 연도별 경험치 테이블
class YearlyExperience(Base):
    __tablename__ = "yearly_experience"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)  # 사용자 ID
    year = Column(Integer, nullable=False)  # 연도
    total_experience = Column(BigInteger, nullable=False)  # 총 경험치
    first_half_evaluation = Column(BigInteger, nullable=False)  # 상반기 평가
    second_half_evaluation = Column(BigInteger, nullable=False)  # 하반기 평가
    job_test = Column(BigInteger, nullable=False)  # 직무 테스트
    leader_test = Column(BigInteger, nullable=False)  # 리더뷰 테스트
    company_project = Column(BigInteger, nullable=False)  # 전사 프로젝트

    user = relationship("User", back_populates="yearly_experience")

# 레벨별 경험치 테이블
class LevelExperience(Base):
    __tablename__ = "level_experience"

    id = Column(Integer, primary_key=True, autoincrement=True)
    job_group = Column(String(50), nullable=False)  # 직군
    level = Column(String(50), nullable=False)  # 레벨
    total_required_experience = Column(BigInteger, nullable=False)  # 총 필요 경험치

# 경험치 유형 테이블
class ExperienceType(Base):
    __tablename__ = "experience_type"

    id = Column(Integer, primary_key=True, autoincrement=True)
    type_name = Column(String(50), nullable=False)  # 유형 이름
    max_experience = Column(BigInteger, nullable=False)  # 최대 경험치


# 인사평가 테이블
class PerformanceEvaluation(Base):
    __tablename__ = "performance_evaluation"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    evaluation_period = Column(String(50), nullable=False)  # 평가 기간
    grade = Column(String(10), nullable=False)  # 등급
    experience_points = Column(BigInteger, nullable=False)  # 경험치
    remarks = Column(String(255))  # 비고

    user = relationship("User", back_populates="performance_evaluations")

# 직무 퀘스트 테이블
class JobQuest(Base):
    __tablename__ = "job_quests"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    score = Column(Float, nullable=False)  # 점수
    experience_points = Column(BigInteger, nullable=False)  # 경험치
    remarks = Column(String(255))  # 비고

    user = relationship("User", back_populates="job_quests")

# 리더뷰 퀘스트 테이블
class LeaderQuest(Base):
    __tablename__ = "leader_quests"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    quest_name = Column(String(100), nullable=False)  # 퀘스트 이름
    experience_points = Column(BigInteger, nullable=False)  # 경험치
    remarks = Column(String(255))  # 비고

    user = relationship("User", back_populates="leader_quests")

# 전사 프로젝트 테이블
class CompanyProject(Base):
    __tablename__ = "company_projects"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)  # 사용자 ID
    project_name = Column(String(100), nullable=False)  # 프로젝트 이름
    experience_points = Column(BigInteger, nullable=False)  # 부여된 경험치
    project_date = Column(DateTime, nullable=False)  # 프로젝트 날짜
    remarks = Column(String(255))  # 비고

    user = relationship("User", back_populates="company_projects")

class JwtToken(Base):
    __tablename__ = "jwt_tokens"

    user_id = Column(Integer, ForeignKey("users.id"), primary_key=True)
    access_token = Column(String(255), nullable=False, index=True)
    refresh_token = Column(String(255), nullable=False)

    user = relationship("User", back_populates="token")