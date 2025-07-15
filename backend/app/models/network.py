from sqlalchemy import Column, String, Integer, DateTime, Boolean, ForeignKey, Float, Text, Table
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.database import Base
import uuid

def generate_uuid():
    return str(uuid.uuid4())

# Association table for network members
network_members = Table(
    "network_members",
    Base.metadata,
    Column("network_id", String, ForeignKey("networks.id")),
    Column("member_id", String, ForeignKey("users.id")),
    Column("level", Integer, nullable=False),
    Column("joined_at", DateTime, default=func.now())
)

class Network(Base):
    __tablename__ = "networks"
    
    id = Column(String, primary_key=True, default=generate_uuid)
    user_id = Column(String, ForeignKey("users.id"), unique=True)
    referral_code = Column(String, unique=True, index=True)
    referred_by = Column(String, ForeignKey("users.id"), nullable=True)
    total_members = Column(Integer, default=0)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="network", foreign_keys=[user_id])
    referrer = relationship("User", foreign_keys=[referred_by])
    members = relationship("User", secondary=network_members, backref="networks")


class Bonus(Base):
    __tablename__ = "bonuses"
    
    id = Column(String, primary_key=True, default=generate_uuid)
    user_id = Column(String, ForeignKey("users.id"))
    amount = Column(Float, nullable=False)
    bonus_type = Column(String, nullable=False)  # referral, level, achievement, etc.
    description = Column(Text, nullable=True)
    reference_id = Column(String, nullable=True)  # For linking to network members, investments, etc.
    is_paid = Column(Boolean, default=False)
    created_at = Column(DateTime, default=func.now())
    paid_at = Column(DateTime, nullable=True)
    
    # Relationships
    user = relationship("User", back_populates="bonuses")


class NOC(Base):
    __tablename__ = "nocs"
    
    id = Column(String, primary_key=True, default=generate_uuid)
    user_id = Column(String, ForeignKey("users.id"))
    document_url = Column(String, nullable=False)
    issue_date = Column(DateTime, default=func.now())
    expiry_date = Column(DateTime, nullable=True)
    is_active = Column(Boolean, default=True)
    
    # Relationships
    user = relationship("User")
