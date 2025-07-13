from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.models.user import User
from app.schemas.user import UserResponse, PasswordReset
from app.core.auth import get_current_active_user, verify_password, get_password_hash

router = APIRouter()

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
