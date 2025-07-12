from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class PlanBase(BaseModel):
    name: str
    min_amount: float
    max_amount: float
    returns_percentage: float = 15.0
    duration_months: int = 12

class PlanCreate(PlanBase):
    pass

class PlanUpdate(BaseModel):
    name: Optional[str] = None
    min_amount: Optional[float] = None
    max_amount: Optional[float] = None
    returns_percentage: Optional[float] = None
    duration_months: Optional[int] = None

class PlanInDB(PlanBase):
    id: str
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True

class Plan(PlanInDB):
    pass
