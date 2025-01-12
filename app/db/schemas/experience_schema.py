from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class ExperienceBase(BaseModel):
    amount: int
    created_at: datetime

class ExperienceCreate(ExperienceBase):
    pass


class Experiences(ExperienceBase):
    data: List[ExperienceBase]