from pydantic import BaseModel, Field, validator
from datetime import datetime
from typing import Optional

class NOCResponse(BaseModel):
    """Schema for NOC document response."""
    user_id: str
    member_id: str
    name: str
    plan_amount: float = Field(default=0.0)
    amount_paid: float = Field(default=0.0)
    total_amount_paid: float = Field(default=0.0)
    incentive_amount: float = Field(default=0.0)
    foreclosure_charges: float = Field(default=0.0)
    final_payable_amount: float = Field(default=0.0)
    due_date: datetime
    company_name: str = "WellVest Financial Services Pvt. Ltd."
    generated_at: datetime
    
    @validator('plan_amount', 'amount_paid', 'total_amount_paid', 'incentive_amount', 
              'foreclosure_charges', 'final_payable_amount', pre=True)
    def validate_float_fields(cls, v):
        if v is None:
            return 0.0
        try:
            return float(v)
        except (ValueError, TypeError):
            return 0.0
    
    @validator('member_id', 'name', 'company_name', pre=True)
    def validate_string_fields(cls, v):
        if v is None or v == "":
            return "N/A"
        return str(v)
    
    class Config:
        orm_mode = True
