from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

# Network Schemas
class NetworkBase(BaseModel):
    referral_code: str
    referred_by: Optional[str] = None
    total_members: int = 0

class NetworkCreate(NetworkBase):
    pass

class NetworkUpdate(BaseModel):
    referral_code: Optional[str] = None
    total_members: Optional[int] = None

class NetworkMemberBase(BaseModel):
    member_id: str
    level: int

class NetworkMemberResponse(NetworkMemberBase):
    joined_at: datetime
    
    class Config:
        orm_mode = True

class NetworkResponse(NetworkBase):
    id: str
    user_id: str
    created_at: datetime
    updated_at: datetime
    
    class Config:
        orm_mode = True

class NetworkWithMembersResponse(NetworkResponse):
    members: List[NetworkMemberResponse] = []
    
    class Config:
        orm_mode = True

# Bonus Schemas
class BonusBase(BaseModel):
    amount: float
    bonus_type: str
    description: Optional[str] = None
    reference_id: Optional[str] = None
    is_paid: bool = False

class BonusCreate(BonusBase):
    pass

class BonusUpdate(BaseModel):
    is_paid: Optional[bool] = None
    paid_at: Optional[datetime] = None

class BonusResponse(BonusBase):
    id: str
    user_id: str
    created_at: datetime
    paid_at: Optional[datetime] = None
    
    class Config:
        orm_mode = True

# NOC Schemas
class NOCBase(BaseModel):
    document_url: str
    expiry_date: Optional[datetime] = None
    is_active: bool = True

class NOCCreate(NOCBase):
    pass

class NOCUpdate(BaseModel):
    document_url: Optional[str] = None
    expiry_date: Optional[datetime] = None
    is_active: Optional[bool] = None

class NOCResponse(NOCBase):
    id: str
    user_id: str
    issue_date: datetime
    
    class Config:
        orm_mode = True
