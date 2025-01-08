from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

# 사용자 기본 정보 스키마
class UserBase(BaseModel):
    employee_id: str
    name: str
    department: str
    job_group: str
    level: str


class UserCreate(UserBase):
    password: str
    public_ip: Optional[str] = None


class User(UserBase):
    id: int
    created_at: datetime
    last_login: Optional[datetime]
    profile_url: Optional[str] = None

    class Config:
        from_attributes = True


# 연도별 경험치 스키마
class YearlyExperienceBase(BaseModel):
    year: int
    total_experience: int
    first_half_evaluation: int
    second_half_evaluation: int
    job_test: int
    leader_test: int
    company_project: int


class YearlyExperienceCreate(YearlyExperienceBase):
    pass


class YearlyExperience(YearlyExperienceBase):
    id: int
    user_id: int

    class Config:
        from_attributes = True


# 레벨별 경험치 스키마
class LevelExperienceBase(BaseModel):
    job_group: str
    level: str
    total_required_experience: int


class LevelExperienceCreate(LevelExperienceBase):
    pass


class LevelExperience(LevelExperienceBase):
    id: int

    class Config:
        from_attributes = True


# 경험치 유형 스키마
class ExperienceTypeBase(BaseModel):
    type_name: str
    max_experience: int
    weight: float


class ExperienceTypeCreate(ExperienceTypeBase):
    pass


class ExperienceType(ExperienceTypeBase):
    id: int

    class Config:
        from_attributes = True


# 인사평가 스키마
class PerformanceEvaluationBase(BaseModel):
    evaluation_period: str
    grade: str
    experience_points: int
    remarks: Optional[str] = None


class PerformanceEvaluationCreate(PerformanceEvaluationBase):
    pass


class PerformanceEvaluation(PerformanceEvaluationBase):
    id: int
    user_id: int

    class Config:
        from_attributes = True


# 직무 퀘스트 스키마
class JobQuestBase(BaseModel):
    score: float
    experience_points: int
    remarks: Optional[str] = None


class JobQuestCreate(JobQuestBase):
    pass


class JobQuest(JobQuestBase):
    id: int
    user_id: int

    class Config:
        from_attributes = True


# 리더뷰 퀘스트 스키마
class LeaderQuestBase(BaseModel):
    quest_name: str
    experience_points: int
    remarks: Optional[str] = None


class LeaderQuestCreate(LeaderQuestBase):
    pass


class LeaderQuest(LeaderQuestBase):
    id: int
    user_id: int

    class Config:
        from_attributes = True


# 전사 프로젝트 스키마
class CompanyProjectBase(BaseModel):
    project_name: str
    experience_points: int
    remarks: Optional[str] = None


class CompanyProjectCreate(CompanyProjectBase):
    pass


class CompanyProject(CompanyProjectBase):
    id: int
    user_id: int

    class Config:
        from_attributes = True


# JWT 토큰 스키마
class JwtToken(BaseModel):
    access_token: str
    refresh_token: str

    class Config:
        from_attributes = True