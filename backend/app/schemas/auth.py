from pydantic import BaseModel, EmailStr, Field, validator
from typing import Optional, Union
from app.utils.phone_utils import normalize_phone_number

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    user_id: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None

class LoginRequest(BaseModel):
    phone: str
    email: Optional[EmailStr] = None
    password: str
    remember_me: bool = False
    
    @validator('phone')
    def validate_login_identifier(cls, v, values):
        # Phone is required for login
        if not v:
            raise ValueError('Phone number is required')
        
        try:
            # Normalize phone number by removing country code prefixes
            return normalize_phone_number(v)
        except ValueError as e:
            raise ValueError(str(e))
    
class PasswordReset(BaseModel):
    current_password: str
    new_password: str = Field(..., min_length=8)
    confirm_password: str
