from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from app.models.payment import PaymentStatus

# Payment Schemas
class PaymentBase(BaseModel):
    user_id: str
    plan_id: str
    amount: float
    upi_ref_id: Optional[str] = None

class PaymentCreate(PaymentBase):
    pass

class PaymentUpdate(BaseModel):
    upi_ref_id: Optional[str] = None
    status: Optional[PaymentStatus] = None
    admin_notes: Optional[str] = None

class PaymentResponse(PaymentBase):
    id: str
    status: PaymentStatus
    admin_notes: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    
    class Config:
        orm_mode = True

class PaymentApproval(BaseModel):
    admin_notes: Optional[str] = None

class PaymentRejection(BaseModel):
    admin_notes: str = Field(..., description="Reason for rejection")

class PaymentWithUpiRef(BaseModel):
    upi_ref_id: str = Field(..., description="UPI reference ID for the payment")
