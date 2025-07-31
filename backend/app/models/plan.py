from sqlalchemy import Column, String, Integer, Float, DateTime, Text, Boolean
from sqlalchemy.sql import func
from app.db.database import Base
import uuid

def generate_uuid():
    return str(uuid.uuid4())

class Plan(Base):
    __tablename__ = "plans"
    
    id = Column(String, primary_key=True, default=generate_uuid)
    name = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    amount = Column(Float, nullable=False)
    duration_months = Column(Integer, nullable=False)
    interest_rate = Column(Float, nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
