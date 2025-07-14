from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class PlanBase(BaseModel):
    name: str
    description: Optional[str] = None
    amount: float
    duration_months: int
    interest_rate: float
    is_active: bool = True

class PlanCreate(PlanBase):
    pass

class PlanUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    amount: Optional[float] = None
    duration_months: Optional[int] = None
    interest_rate: Optional[float] = None
    is_active: Optional[bool] = None

class PlanInDB(PlanBase):
    id: str
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True

class Plan(PlanInDB):
    pass
