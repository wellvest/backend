from pydantic import BaseModel, validator
from typing import Optional
from app.utils.phone_utils import normalize_phone_number

class OTPRequest(BaseModel):
    phone: str
    purpose: str = "verification"  # verification, signup, reset_password
    
    @validator('phone')
    def normalize_phone(cls, v):
        try:
            return normalize_phone_number(v)
        except ValueError as e:
            raise ValueError(str(e))
    
    @validator('purpose')
    def validate_purpose(cls, v):
        valid_purposes = ["verification", "signup", "reset_password"]
        if v not in valid_purposes:
            raise ValueError(f"Purpose must be one of: {', '.join(valid_purposes)}")
        return v

class OTPVerify(BaseModel):
    phone: str
    otp: str
    
    @validator('phone')
    def normalize_phone(cls, v):
        try:
            return normalize_phone_number(v)
        except ValueError as e:
            raise ValueError(str(e))

class ForgotPasswordRequest(BaseModel):
    phone: str
    
    @validator('phone')
    def normalize_phone(cls, v):
        try:
            return normalize_phone_number(v)
        except ValueError as e:
            raise ValueError(str(e))

class ResetPasswordWithOTP(BaseModel):
    phone: str
    otp: str
    new_password: str
    confirm_password: str
    
    @validator('phone')
    def normalize_phone(cls, v):
        try:
            return normalize_phone_number(v)
        except ValueError as e:
            raise ValueError(str(e))
    
    @validator('new_password')
    def password_min_length(cls, v):
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        return v
    
    @validator('confirm_password')
    def passwords_match(cls, v, values):
        if 'new_password' in values and v != values['new_password']:
            raise ValueError('Passwords do not match')
        return v
