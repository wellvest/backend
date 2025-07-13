from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from app.models.investment import InvestmentStatus

# Investment Schemas
class InvestmentBase(BaseModel):
    plan_name: str
    amount: float
    duration_months: int
    status: InvestmentStatus = InvestmentStatus.ACTIVE

class InvestmentCreate(InvestmentBase):
    pass

class InvestmentUpdate(BaseModel):
    plan_name: Optional[str] = None
    amount: Optional[float] = None
    duration_months: Optional[int] = None
    status: Optional[InvestmentStatus] = None
    end_date: Optional[datetime] = None
    returns: Optional[float] = None

class InvestmentResponse(InvestmentBase):
    id: str
    user_id: str
    start_date: datetime
    end_date: Optional[datetime] = None
    returns: float
    created_at: datetime
    updated_at: datetime
    
    class Config:
        orm_mode = True

# Team Investment Schemas
class TeamInvestmentBase(BaseModel):
    investment_id: str
    team_member_id: str
    amount: float
    level: int

class TeamInvestmentCreate(TeamInvestmentBase):
    pass

class TeamInvestmentResponse(TeamInvestmentBase):
    id: str
    created_at: datetime
    
    class Config:
        orm_mode = True

# Investment with Team Investments Response
class InvestmentWithTeamResponse(InvestmentResponse):
    team_investments: List[TeamInvestmentResponse] = []
    
    class Config:
        orm_mode = True
