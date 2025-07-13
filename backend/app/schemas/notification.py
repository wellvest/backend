from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class NotificationBase(BaseModel):
    title: str
    message: str
    type: str = Field(..., description="Type of notification: success, info, warning")


class NotificationCreate(NotificationBase):
    user_id: str


class NotificationUpdate(BaseModel):
    read: Optional[bool] = None


class NotificationResponse(NotificationBase):
    id: str
    user_id: str
    read: bool
    created_at: datetime

    class Config:
        from_attributes = True
