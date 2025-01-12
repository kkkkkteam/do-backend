from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class ExperienceBase(BaseModel):
    amount: int

class ExperienceCreate(ExperienceBase):
    employee_id: str

class Experience(ExperienceBase):
    created_at: datetime

class Experiences(BaseModel):
    total_experience: int
    data: List[Experience]