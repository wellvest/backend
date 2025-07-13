from pydantic import BaseModel, EmailStr, Field, validator
from typing import Optional, List
from datetime import datetime
from app.utils.phone_utils import normalize_phone_number

# Base User Schema
class UserBase(BaseModel):
    name: str
    phone: str  # Phone is now required
    email: Optional[EmailStr] = None  # Email is now optional
    date_of_birth: Optional[str] = None
    gender: Optional[str] = None
    avatar: Optional[str] = None

# Schema for creating a new user
class UserCreate(UserBase):
    password: str
    referral_code: Optional[str] = None
    
    @validator('password')
    def password_min_length(cls, v):
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        return v
    
    @validator('phone')
    def normalize_phone(cls, v):
        try:
            return normalize_phone_number(v)
        except ValueError as e:
            raise ValueError(str(e))

# Schema for updating user information
class UserUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    date_of_birth: Optional[str] = None
    gender: Optional[str] = None
    avatar: Optional[str] = None
    
    @validator('phone')
    def normalize_phone(cls, v):
        if v is None:
            return v
        try:
            return normalize_phone_number(v)
        except ValueError as e:
            raise ValueError(str(e))

# Schema for user response
class UserResponse(UserBase):
    id: str
    member_id: str
    join_date: datetime
    is_active: bool
    referral_code: Optional[str] = None
    
    class Config:
        orm_mode = True

# Profile Schemas
class ProfileBase(BaseModel):
    plan_amount: float = 0.0
    kyc_verified: bool = False
    kyc_document_type: Optional[str] = None
    kyc_document_number: Optional[str] = None
    kyc_document_url: Optional[str] = None

class ProfileCreate(ProfileBase):
    pass

class ProfileUpdate(BaseModel):
    plan_amount: Optional[float] = None
    kyc_verified: Optional[bool] = None
    kyc_document_type: Optional[str] = None
    kyc_document_number: Optional[str] = None
    kyc_document_url: Optional[str] = None

class ProfileResponse(ProfileBase):
    id: str
    user_id: str
    
    class Config:
        orm_mode = True

# Address Schemas
class AddressBase(BaseModel):
    address_type: str
    address_line1: str
    address_line2: Optional[str] = None
    city: str
    state: str
    zip_code: str
    country: str
    notes: Optional[str] = None
    is_default: bool = False

class AddressCreate(AddressBase):
    pass

class AddressUpdate(BaseModel):
    address_type: Optional[str] = None
    address_line1: Optional[str] = None
    address_line2: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    zip_code: Optional[str] = None
    country: Optional[str] = None
    notes: Optional[str] = None
    is_default: Optional[bool] = None

class AddressResponse(AddressBase):
    id: str
    user_id: str
    
    class Config:
        orm_mode = True

# Bank Details Schemas
class BankDetailBase(BaseModel):
    account_holder_name: str
    account_number: str
    bank_name: str
    branch_name: Optional[str] = None
    ifsc_code: str
    is_default: bool = False

class BankDetailCreate(BankDetailBase):
    pass

class BankDetailUpdate(BaseModel):
    account_holder_name: Optional[str] = None
    account_number: Optional[str] = None
    bank_name: Optional[str] = None
    branch_name: Optional[str] = None
    ifsc_code: Optional[str] = None
    is_default: Optional[bool] = None

class BankDetailResponse(BankDetailBase):
    id: str
    user_id: str
    
    class Config:
        orm_mode = True

# Password Reset Schema
class PasswordReset(BaseModel):
    current_password: str
    new_password: str
    confirm_password: str
    
    @validator('new_password')
    def password_min_length(cls, v):
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        return v

# Complete User Profile Response
class UserProfileResponse(BaseModel):
    user: UserResponse
    profile: Optional[ProfileResponse] = None
    addresses: List[AddressResponse] = []
    bank_details: List[BankDetailResponse] = []
    
    class Config:
        orm_mode = True
