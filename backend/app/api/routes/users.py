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
    from app.utils.url_utils import ensure_relative_url
    
    # Ensure avatar URL is relative before returning
    if current_user.avatar:
        current_user.avatar = ensure_relative_url(current_user.avatar)
    
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
    
    # Ensure avatar URL is relative before returning
    if current_user.avatar:
        current_user.avatar = ensure_relative_url(current_user.avatar)
    
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
    file_extension = os.path.splitext(avatar_file.filename)[1].lower() if avatar_file.filename else ".jpg"
    
    if file_extension not in allowed_extensions:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File type not allowed. Allowed types: {', '.join(allowed_extensions)}"
        )
    
    # Generate unique filename with UUID to prevent collisions
    import uuid
    unique_id = str(uuid.uuid4())
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    filename = f"{unique_id}_{timestamp}{file_extension}"
    
    # Save the uploaded file
    try:
        upload_dir = ensure_upload_dir("avatars")
        file_path = os.path.join(upload_dir, filename)
        
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(avatar_file.file, buffer)
            
        # Set proper file permissions
        try:
            os.chmod(file_path, 0o644)  # rw-r--r--
        except Exception as e:
            print(f"Warning: Could not set permissions on {file_path}: {e}")
            
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error saving file: {str(e)}"
        )
    finally:
        avatar_file.file.close()
    
    # Update user with avatar URL - always store as relative path
    avatar_url = f"/uploads/avatars/{filename}"
    current_user.avatar = avatar_url
    
    db.add(current_user)
    db.commit()
    db.refresh(current_user)
    
    print(f"Avatar uploaded successfully: {avatar_url}")
    
    # Ensure avatar URL is relative before returning
    from app.utils.url_utils import ensure_relative_url
    if current_user.avatar:
        current_user.avatar = ensure_relative_url(current_user.avatar)
    
    return current_user

@router.get("/users/profile", response_model=UserProfileResponse)
@router.get("/users/me/profile", response_model=UserProfileResponse)
async def get_user_profile(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get complete user profile including addresses and bank details."""
    # Ensure avatar URL is relative before returning
    from app.utils.url_utils import ensure_relative_url
    if current_user.avatar:
        current_user.avatar = ensure_relative_url(current_user.avatar)
    
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


# Ensure the upload directory exists with proper permissions
def ensure_upload_dir(dir_type="kyc"):
    # Use absolute path for consistency
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
    upload_dir = os.path.join(base_dir, "uploads", dir_type)
    os.makedirs(upload_dir, exist_ok=True)
    
    # Set proper permissions (readable by web server)
    try:
        os.chmod(upload_dir, 0o755)  # rwxr-xr-x
    except Exception as e:
        print(f"Warning: Could not set permissions on {upload_dir}: {e}")
        
    return upload_dir


# Import at the top level to avoid repeated imports in each function
from app.utils.url_utils import ensure_relative_url


@router.post("/users/me/kyc", response_model=UserProfileResponse)
async def update_kyc_documents(
    document_type: str = Form(...),
    document_number: str = Form(...),
    document_file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Upload and update KYC documents for the current user."""
    # Validate file type
    allowed_extensions = [".jpg", ".jpeg", ".png", ".pdf"]
    file_extension = os.path.splitext(document_file.filename)[1].lower() if document_file.filename else ".jpg"
    
    if file_extension not in allowed_extensions:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File type not allowed. Allowed types: {', '.join(allowed_extensions)}"
        )
    
    # Generate unique filename with UUID to prevent collisions
    import uuid
    unique_id = str(uuid.uuid4())
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    filename = f"{unique_id}_{timestamp}{file_extension}"
    
    # Save the uploaded file
    try:
        upload_dir = ensure_upload_dir()
        file_path = os.path.join(upload_dir, filename)
        
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(document_file.file, buffer)
            
        # Set proper file permissions
        try:
            os.chmod(file_path, 0o644)  # rw-r--r--
        except Exception as e:
            print(f"Warning: Could not set permissions on {file_path}: {e}")
            
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error saving file: {str(e)}"
        )
    finally:
        document_file.file.close()
    
    document_url = f"/uploads/kyc/{filename}"
    
    # Get or create user profile
    user_profile = db.query(Profile).filter(Profile.user_id == current_user.id).first()
    if not user_profile:
        user_profile = Profile(user_id=current_user.id)
    
    # Update profile with document info
    user_profile.kyc_document_type = document_type
    user_profile.kyc_document_number = document_number
    user_profile.kyc_document_url = document_url
    user_profile.kyc_verified = False  # Reset verification status when document is updated
    user_profile.kyc_submitted_at = datetime.now()
    
    db.add(user_profile)
    db.commit()
    db.refresh(user_profile)
    
    print(f"KYC document uploaded successfully: {document_url}")
    
    # Send KYC submission confirmation email to the user
    try:
        email_service.send_kyc_submission_notification(current_user.email, current_user.name)
        
        # Notify admin about the new KYC submission
        email_service.notify_admin_of_kyc_submission(
            user_email=current_user.email,
            user_name=current_user.name,
            document_type=document_type
        )
    except Exception as e:
        # Log the error but don't fail the request
        print(f"Error sending KYC notification emails: {e}")
    
    return {"user": current_user, "profile": user_profile}


@router.get("/admin/users", response_model=List[UserProfileResponse])
async def get_all_users(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_superuser),
    skip: int = 0,
    limit: int = 100
):
    """Get all users (admin only)."""
    from app.utils.url_utils import ensure_relative_url
    
    users = db.query(User).offset(skip).limit(limit).all()
    result = []
    for user in users:
        # Ensure avatar URL is relative
        if user.avatar:
            user.avatar = ensure_relative_url(user.avatar)
            
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
    from app.utils.url_utils import ensure_relative_url
    
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
    
    # Ensure avatar URL is relative
    if user.avatar:
        user.avatar = ensure_relative_url(user.avatar)
    
    return {"user": user, "profile": user.profile, 
            "addresses": user.addresses, "bank_details": user.bank_details}
