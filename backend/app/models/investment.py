from sqlalchemy import Column, String, Integer, DateTime, Boolean, ForeignKey, Float, Text, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.database import Base
import uuid
import enum

def generate_uuid():
    return str(uuid.uuid4())

class InvestmentStatus(str, enum.Enum):
    ACTIVE = "active"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    PENDING = "pending"

class Investment(Base):
    __tablename__ = "investments"
    
    id = Column(String, primary_key=True, default=generate_uuid)
    user_id = Column(String, ForeignKey("users.id"))
    plan_name = Column(String, nullable=False)
    amount = Column(Float, nullable=False)
    duration_months = Column(Integer, nullable=False)
    start_date = Column(DateTime, default=func.now())
    end_date = Column(DateTime, nullable=True)
    status = Column(Enum(InvestmentStatus), default=InvestmentStatus.ACTIVE)
    returns = Column(Float, default=0.0)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="investments")
    team_investments = relationship("TeamInvestment", back_populates="investment")


class TeamInvestment(Base):
    __tablename__ = "team_investments"
    
    id = Column(String, primary_key=True, default=generate_uuid)
    investment_id = Column(String, ForeignKey("investments.id"))
    team_member_id = Column(String, ForeignKey("users.id"))
    amount = Column(Float, nullable=False)
    level = Column(Integer, nullable=False)  # Level in the network hierarchy
    created_at = Column(DateTime, default=func.now())
    
    # Relationships
    investment = relationship("Investment", back_populates="team_investments")
    team_member = relationship("User")
