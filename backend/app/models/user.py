from sqlalchemy import Column, String, Integer, DateTime, Boolean, ForeignKey, Float, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.database import Base
import uuid

def generate_uuid():
    return str(uuid.uuid4())

class User(Base):
    __tablename__ = "users"
    
    id = Column(String, primary_key=True, default=generate_uuid)
    member_id = Column(String, unique=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=True)  # Email is now optional
    hashed_password = Column(String, nullable=False)
    phone = Column(String, unique=True, index=True, nullable=False)  # Phone is now required and unique
    date_of_birth = Column(String)
    gender = Column(String)
    join_date = Column(DateTime, default=func.now())
    is_active = Column(Boolean, default=True)
    avatar = Column(String, nullable=True)
    referral_code = Column(String, unique=True, index=True)
    referrer_id = Column(String, ForeignKey("users.id"), nullable=True)
    
    # Relationships
    profile = relationship("Profile", back_populates="user", uselist=False)
    addresses = relationship("Address", back_populates="user")
    bank_details = relationship("BankDetail", back_populates="user")
    investments = relationship("Investment", back_populates="user")
    income_wallet = relationship("IncomeWallet", back_populates="user", uselist=False)
    shopping_wallet = relationship("ShoppingWallet", back_populates="user", uselist=False)
    bonuses = relationship("Bonus", back_populates="user")
    network = relationship("Network", back_populates="user", uselist=False, foreign_keys="[Network.user_id]")
    # Notifications are handled from the Notification model side
    
    # Referral relationships
    referrer = relationship("User", remote_side=[id], backref="referrals")


class Profile(Base):
    __tablename__ = "profiles"
    
    id = Column(String, primary_key=True, default=generate_uuid)
    user_id = Column(String, ForeignKey("users.id"), unique=True)
    plan_amount = Column(Float, default=0.0)
    kyc_verified = Column(Boolean, default=False)
    kyc_document_type = Column(String, nullable=True)
    kyc_document_number = Column(String, nullable=True)
    kyc_document_url = Column(String, nullable=True)
    
    # Relationships
    user = relationship("User", back_populates="profile")


class Address(Base):
    __tablename__ = "addresses"
    
    id = Column(String, primary_key=True, default=generate_uuid)
    user_id = Column(String, ForeignKey("users.id"))
    address_type = Column(String, nullable=False)  # home, office, etc.
    address_line1 = Column(String, nullable=False)
    address_line2 = Column(String, nullable=True)
    city = Column(String, nullable=False)
    state = Column(String, nullable=False)
    zip_code = Column(String, nullable=False)
    country = Column(String, nullable=False)
    notes = Column(Text, nullable=True)
    is_default = Column(Boolean, default=False)
    
    # Relationships
    user = relationship("User", back_populates="addresses")


class BankDetail(Base):
    __tablename__ = "bank_details"
    
    id = Column(String, primary_key=True, default=generate_uuid)
    user_id = Column(String, ForeignKey("users.id"))
    account_holder_name = Column(String, nullable=False)
    account_number = Column(String, nullable=False)
    bank_name = Column(String, nullable=False)
    branch_name = Column(String, nullable=True)
    ifsc_code = Column(String, nullable=False)
    is_default = Column(Boolean, default=False)
    
    # Relationships
    user = relationship("User", back_populates="bank_details")
