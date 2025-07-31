from sqlalchemy import Column, String, Integer, DateTime, Boolean, ForeignKey, Float, Text, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.database import Base
import uuid
import enum

def generate_uuid():
    return str(uuid.uuid4())

class TransactionType(str, enum.Enum):
    CREDIT = "credit"
    DEBIT = "debit"

class TransactionStatus(str, enum.Enum):
    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"
    REJECTED = "rejected"

class IncomeWallet(Base):
    __tablename__ = "income_wallets"
    
    id = Column(String, primary_key=True, default=generate_uuid)
    user_id = Column(String, ForeignKey("users.id"), unique=True)
    balance = Column(Float, default=0.0)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="income_wallet")
    transactions = relationship("IncomeTransaction", back_populates="wallet")


class IncomeTransaction(Base):
    __tablename__ = "income_transactions"
    
    id = Column(String, primary_key=True, default=generate_uuid)
    wallet_id = Column(String, ForeignKey("income_wallets.id"))
    amount = Column(Float, nullable=False)
    transaction_type = Column(Enum(TransactionType), nullable=False)
    status = Column(Enum(TransactionStatus), default=TransactionStatus.PENDING)
    description = Column(Text, nullable=True)
    reference_id = Column(String, nullable=True)  # For linking to bonuses, investments, etc.
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relationships
    wallet = relationship("IncomeWallet", back_populates="transactions")


class ShoppingWallet(Base):
    __tablename__ = "shopping_wallets"
    
    id = Column(String, primary_key=True, default=generate_uuid)
    user_id = Column(String, ForeignKey("users.id"), unique=True)
    balance = Column(Float, default=0.0)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="shopping_wallet")
    transactions = relationship("ShoppingTransaction", back_populates="wallet")
    vouchers = relationship("ShoppingVoucher", back_populates="wallet")


class ShoppingTransaction(Base):
    __tablename__ = "shopping_transactions"
    
    id = Column(String, primary_key=True, default=generate_uuid)
    wallet_id = Column(String, ForeignKey("shopping_wallets.id"))
    amount = Column(Float, nullable=False)
    transaction_type = Column(Enum(TransactionType), nullable=False)
    status = Column(Enum(TransactionStatus), default=TransactionStatus.PENDING)
    description = Column(Text, nullable=True)
    reference_id = Column(String, nullable=True)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relationships
    wallet = relationship("ShoppingWallet", back_populates="transactions")


class ShoppingVoucher(Base):
    __tablename__ = "shopping_vouchers"
    
    id = Column(String, primary_key=True, default=generate_uuid)
    wallet_id = Column(String, ForeignKey("shopping_wallets.id"))
    code = Column(String, nullable=False, unique=True)
    amount = Column(Float, nullable=False)
    is_used = Column(Boolean, default=False)
    expiry_date = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=func.now())
    used_at = Column(DateTime, nullable=True)
    
    # Relationships
    wallet = relationship("ShoppingWallet", back_populates="vouchers")
