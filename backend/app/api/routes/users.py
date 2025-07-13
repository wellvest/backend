from fastapi import APIRouter, Depends, HTTPException, status, File, UploadFile, Form
from sqlalchemy.orm import Session
from typing import List, Optional
import os
import shutil
from datetime import datetime
from fastapi.staticfiles import StaticFiles

from app.core.auth import get_current_active_user, get_current_active_superuser
from app.db.database import get_db
from app.models.user import User, Profile
from app.schemas.user import UserResponse, UserUpdate, UserProfileResponse, ProfileUpdate
from app.services.email_service import email_service

router = APIRouter()

@router.get("/users/me", response_model=UserResponse)
async def read_users_me(current_user: User = Depends(get_current_active_user)):
    """Get current user information."""
    return current_user

@router.put("/users/me", response_model=UserResponse)
async def update_user_me(
    user_in: UserUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Update current user information."""
    # Check if email is being updated and if it's already taken
    if user_in.email and user_in.email != current_user.email:
        user_with_email = db.query(User).filter(User.email == user_in.email).first()
        if user_with_email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
    
    # Update user attributes
    for key, value in user_in.dict(exclude_unset=True).items():
        if value is not None:
            setattr(current_user, key, value)
    
    db.add(current_user)
    db.commit()
    db.refresh(current_user)
    
    return current_user


@router.post("/users/me/avatar", response_model=UserResponse)
async def upload_avatar(
    avatar_file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Upload profile avatar image for the current user."""
    # Validate file type
    allowed_extensions = [".jpg", ".jpeg", ".png", ".gif"]
    file_extension = os.path.splitext(avatar_file.filename)[1].lower()
    
    if file_extension not in allowed_extensions:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File type not allowed. Allowed types: {', '.join(allowed_extensions)}"
        )
    
    # Save the uploaded file
    upload_dir = ensure_upload_dir("avatars")
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    filename = f"{current_user.id}_{timestamp}{file_extension}"
    file_path = os.path.join(upload_dir, filename)
    
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(avatar_file.file, buffer)
    
    # Update user with avatar URL
    avatar_url = f"/uploads/avatars/{filename}"
    current_user.avatar = avatar_url
    
    db.add(current_user)
    db.commit()
    db.refresh(current_user)
    
    return current_user

@router.get("/users/profile", response_model=UserProfileResponse)
@router.get("/users/me/profile", response_model=UserProfileResponse)
async def get_user_profile(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get complete user profile including addresses and bank details."""
    # The ORM relationships will handle fetching the related data
    return {"user": current_user, "profile": current_user.profile, 
            "addresses": current_user.addresses, "bank_details": current_user.bank_details}


@router.get("/users/me/current-plan")
async def get_current_plan(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get the current plan for the logged-in user."""
    if not current_user.profile or not current_user.profile.current_plan_id:
        return {"has_plan": False, "plan": None, "plan_amount": 0}
    
    from app.models.plan import Plan
    plan = db.query(Plan).filter(Plan.id == current_user.profile.current_plan_id).first()
    
    if not plan:
        return {"has_plan": False, "plan": None, "plan_amount": current_user.profile.plan_amount}
    
    return {
        "has_plan": True,
        "plan": plan,
        "plan_amount": current_user.profile.plan_amount
    }


# Ensure the upload directory exists
def ensure_upload_dir(dir_type="kyc"):
    upload_dir = os.path.join("uploads", dir_type)
    os.makedirs(upload_dir, exist_ok=True)
    return upload_dir


@router.post("/users/me/kyc", response_model=UserProfileResponse)
async def update_kyc_documents(
    document_type: str = Form(...),
    document_number: str = Form(...),
    document_file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Upload and update KYC documents for the current user."""
    # Ensure user has a profile
    if not current_user.profile:
        profile = Profile(user_id=current_user.id)
        db.add(profile)
        db.commit()
        db.refresh(current_user)
    
    # Save the uploaded file
    upload_dir = ensure_upload_dir()
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    file_extension = os.path.splitext(document_file.filename)[1]
    filename = f"{current_user.id}_{timestamp}{file_extension}"
    file_path = os.path.join(upload_dir, filename)
    
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(document_file.file, buffer)
    
    # Update profile with KYC information
    document_url = f"/uploads/kyc/{filename}"
    
    # Update profile
    profile = current_user.profile
    profile.kyc_document_type = document_type
    profile.kyc_document_number = document_number
    profile.kyc_document_url = document_url
    profile.kyc_verified = False  # Set to false until verified by admin
    
    db.add(profile)
    db.commit()
    db.refresh(current_user)
    
    # Send KYC submission confirmation email to the user
    email_service.send_kyc_submission_notification(current_user.email, current_user.name)
    
    # Notify admin about the new KYC submission
    email_service.notify_admin_of_kyc_submission(
        user_email=current_user.email,
        user_name=current_user.name,
        document_type=document_type
    )
    
    return {"user": current_user, "profile": current_user.profile, 
            "addresses": current_user.addresses, "bank_details": current_user.bank_details}


@router.get("/admin/users", response_model=List[UserProfileResponse])
async def get_all_users(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_superuser),
    skip: int = 0,
    limit: int = 100
):
    """Get all users (admin only)."""
    users = db.query(User).offset(skip).limit(limit).all()
    result = []
    for user in users:
        result.append({
            "user": user,
            "profile": user.profile,
            "addresses": user.addresses,
            "bank_details": user.bank_details
        })
    return result


@router.put("/admin/users/{user_id}/kyc-verify", response_model=UserProfileResponse)
async def verify_kyc(
    user_id: str,
    verified: bool,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_superuser)
):
    """Verify or reject KYC documents (admin only)."""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    if not user.profile:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User has no profile"
        )
    
    # Update verification status
    user.profile.kyc_verified = verified
    
    db.add(user.profile)
    db.commit()
    db.refresh(user)
    
    # Send email notification to user about KYC verification result
    email_service.send_kyc_verification_result(
        user_email=user.email,
        user_name=user.name,
        is_verified=verified
    )
    
    return {"user": user, "profile": user.profile, 
            "addresses": user.addresses, "bank_details": user.bank_details}
