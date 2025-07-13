from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.core.auth import create_access_token, get_password_hash, verify_password, get_current_active_user
from app.core.config import settings
from app.db.database import get_db
from app.models.user import User, Profile
from app.schemas.auth import Token, LoginRequest, PasswordReset
from app.schemas.user import UserCreate, UserResponse
from app.services.email_service import email_service
from app.utils.phone_utils import normalize_phone_number, is_valid_phone_number

router = APIRouter()

@router.post("/auth/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register_user(user_in: UserCreate, db: Session = Depends(get_db)):
    """Register a new user."""
    # Check if phone number already exists
    db_user = db.query(User).filter(User.phone == user_in.phone).first()
    if db_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Phone number already registered"
        )
    
    # If email is provided, check if it's already registered
    if user_in.email:
        email_user = db.query(User).filter(User.email == user_in.email).first()
        if email_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
    
    # Generate a unique member ID (you might want to implement a more sophisticated logic)
    last_user = db.query(User).order_by(User.member_id.desc()).first()
    if last_user and last_user.member_id.isdigit():
        member_id = str(int(last_user.member_id) + 1).zfill(8)
    else:
        member_id = "10000001"  # Starting member ID
    
    # Generate a unique referral code based on member_id
    referral_code = f"WV{member_id}"
    
    # Check if a referral code was provided
    referrer_id = None
    if user_in.referral_code:
        referrer = db.query(User).filter(User.referral_code == user_in.referral_code).first()
        if referrer:
            referrer_id = referrer.id
    
    # Create new user
    hashed_password = get_password_hash(user_in.password)
    db_user = User(
        email=user_in.email,
        name=user_in.name,
        hashed_password=hashed_password,
        member_id=member_id,
        phone=user_in.phone,
        date_of_birth=user_in.date_of_birth,
        gender=user_in.gender,
        avatar=user_in.avatar,
        referral_code=referral_code,
        referrer_id=referrer_id
    )
    
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    # Automatically create a profile for the user
    db_profile = Profile(user_id=db_user.id)
    db.add(db_profile)
    db.commit()
    db.refresh(db_profile)
    
    # Send welcome email to the new user
    email_service.send_welcome_email(db_user.email, db_user.name)
    
    # If user signed up with a referral code, notify the referrer
    if referrer_id:
        referrer = db.query(User).filter(User.id == referrer_id).first()
        if referrer:
            email_service.send_referral_notification(
                referrer_email=referrer.email,
                referrer_name=referrer.name,
                new_user_name=db_user.name
            )
    
    return db_user

@router.post("/auth/login", response_model=Token)
def login_for_access_token(login_data: LoginRequest, db: Session = Depends(get_db)):
    """Login and get access token using phone number."""
    # Phone number is already normalized in the LoginRequest validator
    
    # Authenticate user by phone number
    user = db.query(User).filter(User.phone == login_data.phone).first()
    if not user or not verify_password(login_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect phone number or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Set token expiration based on remember_me flag
    if login_data.remember_me:
        access_token_expires = timedelta(days=30)  # 30 days for remember me
    else:
        access_token_expires = timedelta(minutes=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES)
    
    # Create access token with both user ID and phone number
    token_data = {"sub": user.id}
    if user.phone:
        token_data["phone"] = user.phone
    if user.email:
        token_data["email"] = user.email
        
    access_token = create_access_token(
        data=token_data,
        expires_delta=access_token_expires
    )
    
    return {"access_token": access_token, "token_type": "bearer"}

# OAuth2 compatible login endpoint for OpenAPI UI
@router.post("/auth/token", response_model=Token)
def login_for_access_token_oauth(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    """OAuth2 compatible token login, get an access token for future requests."""
    normalized_username = form_data.username
    
    # Try to normalize the username if it looks like a phone number
    try:
        if is_valid_phone_number(form_data.username):
            normalized_username = normalize_phone_number(form_data.username)
    except ValueError:
        # If normalization fails, just use the original username
        pass
    
    # Try to find user by phone number first (username field contains phone)
    user = db.query(User).filter(User.phone == normalized_username).first()
    
    # If not found by phone, try email as fallback
    if not user:
        user = db.query(User).filter(User.email == form_data.username).first()
        
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect phone number/email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES)
    
    # Create token with both user ID and phone number
    token_data = {"sub": user.id}
    if user.phone:
        token_data["phone"] = user.phone
    if user.email:
        token_data["email"] = user.email
        
    access_token = create_access_token(
        data=token_data,
        expires_delta=access_token_expires
    )
    
    return {"access_token": access_token, "token_type": "bearer"}
@router.post("/auth/reset-password", response_model=UserResponse)
async def reset_password(
    password_data: PasswordReset,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Reset password for the current user."""
    # Verify current password
    if not verify_password(password_data.current_password, current_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Current password is incorrect"
        )
    
    # Verify that new password and confirm password match
    if password_data.new_password != password_data.confirm_password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="New password and confirm password do not match"
        )
    
    # Update password
    current_user.hashed_password = get_password_hash(password_data.new_password)
    db.add(current_user)
    db.commit()
    db.refresh(current_user)
    
    return current_user
