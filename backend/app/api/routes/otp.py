import logging
import os
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from dotenv import load_dotenv

from app.db.database import get_db
from app.models.user import User
from app.schemas.otp import OTPRequest, OTPVerify, ForgotPasswordRequest, ResetPasswordWithOTP
from app.services.sms_service import sms_service
from app.core.auth import get_password_hash
from app.utils.notification_utils import send_phone_verification_notification

# Load environment variables
load_dotenv()

logger = logging.getLogger(__name__)

# Helper function to normalize phone numbers
def normalize_phone(phone: str) -> str:
    """Normalize phone number by removing spaces and ensuring it starts with +"""
    phone = phone.strip().replace(" ", "")
    if not phone.startswith("+"):
        phone = "+" + phone
    return phone

router = APIRouter()

# Check if OTP verification is enabled
otp_verification_enabled = os.getenv("OTP_VERIFICATION_ENABLED", "true").lower() == "true"

@router.get("/auth/otp-status")
def get_otp_status():
    """Get the current status of OTP verification"""
    return {"otp_verification_enabled": otp_verification_enabled}

@router.post("/auth/send-otp", status_code=status.HTTP_200_OK)
def send_otp(otp_request: OTPRequest, db: Session = Depends(get_db)):
    """Send OTP to the user's phone number."""
    try:
        # Check if OTP verification is enabled
        if not otp_verification_enabled and otp_request.purpose == "signup":
            logger.info("OTP verification is disabled for signup. Skipping OTP generation.")
            return {"message": "OTP verification is disabled", "otp_verification_enabled": False}
            
        # Normalize phone number
        normalized_phone = normalize_phone(otp_request.phone)
        logger.info(f"Sending OTP for purpose: {otp_request.purpose} to phone: {normalized_phone}")
        
        # Check if phone number exists for reset_password purpose
        if otp_request.purpose == "reset_password":
            user = db.query(User).filter(User.phone == normalized_phone).first()
            if not user:
                logger.warning(f"Reset password attempt for non-registered phone: {normalized_phone}")
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Phone number not registered"
                )
        
        # For signup, check if phone number is already registered
        if otp_request.purpose == "signup":
            user = db.query(User).filter(User.phone == normalized_phone).first()
            if user:
                logger.warning(f"Signup attempt with already registered phone: {normalized_phone}")
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Phone number already registered"
                )
        
        # Generate and send OTP
        sms_service.send_otp(normalized_phone, otp_request.purpose)
        return {"message": "OTP sent successfully", "otp_verification_enabled": otp_verification_enabled}
    except HTTPException:
        # Re-raise HTTP exceptions as they are already properly formatted
        raise
    except Exception as e:
        logger.error(f"Error sending OTP: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to send OTP: {str(e)}"
        )

@router.post("/auth/verify-otp", status_code=status.HTTP_200_OK)
def verify_otp(otp_verify: OTPVerify, db: Session = Depends(get_db)):
    """Verify OTP sent to the user's phone."""
    try:
        # Check if OTP verification is disabled
        if not otp_verification_enabled:
            logger.info("OTP verification is disabled. Automatically validating OTP.")
            return {"message": "OTP verification is disabled", "otp_verification_enabled": False}
            
        # Normalize phone number
        normalized_phone = normalize_phone(otp_verify.phone)
        logger.info(f"Verifying OTP for phone: {normalized_phone}")
        
        is_valid = sms_service.verify_otp(normalized_phone, otp_verify.otp)
        
        if not is_valid:
            logger.warning(f"Invalid OTP verification attempt for phone: {normalized_phone}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid or expired OTP"
            )
        
        # If this is for an existing user, send a notification
        user = db.query(User).filter(User.phone == normalized_phone).first()
        if user:
            send_phone_verification_notification(db, user.id)
            logger.info(f"Phone verification notification sent to user: {user.id}")
        
        logger.info(f"OTP verified successfully for phone: {normalized_phone}")
        return {"message": "OTP verified successfully", "otp_verification_enabled": otp_verification_enabled}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error verifying OTP: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to verify OTP: {str(e)}"
        )

@router.post("/auth/forgot-password", status_code=status.HTTP_200_OK)
def forgot_password(request: ForgotPasswordRequest, db: Session = Depends(get_db)):
    """Send OTP for password reset."""
    try:
        # Normalize phone number
        normalized_phone = normalize_phone(request.phone)
        logger.info(f"Forgot password request for phone: {normalized_phone}")
        
        # Check if user exists
        user = db.query(User).filter(User.phone == normalized_phone).first()
        if not user:
            logger.warning(f"Forgot password attempt for non-registered phone: {normalized_phone}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Phone number not registered"
            )
        
        # Generate and send OTP
        sms_service.send_otp(normalized_phone, "reset_password")
        logger.info(f"Password reset OTP sent successfully to: {normalized_phone}")
        return {"message": "Password reset OTP sent successfully"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error sending password reset OTP: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to send password reset OTP: {str(e)}"
        )

@router.post("/auth/reset-password-with-otp", status_code=status.HTTP_200_OK)
def reset_password_with_otp(request: ResetPasswordWithOTP, db: Session = Depends(get_db)):
    """Reset password using OTP verification."""
    try:
        # Normalize phone number
        normalized_phone = normalize_phone(request.phone)
        logger.info(f"Reset password with OTP request for phone: {normalized_phone}")
        
        # Verify OTP
        is_valid = sms_service.verify_otp(normalized_phone, request.otp)
        
        if not is_valid:
            logger.warning(f"Invalid OTP for password reset: {normalized_phone}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid or expired OTP"
            )
        
        # Check if passwords match
        if request.new_password != request.confirm_password:
            logger.warning(f"Password mismatch in reset password: {normalized_phone}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Passwords do not match"
            )
        
        # Check if user exists
        user = db.query(User).filter(User.phone == normalized_phone).first()
        if not user:
            logger.warning(f"User not found for password reset: {normalized_phone}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Update password
        hashed_password = get_password_hash(request.new_password)
        user.hashed_password = hashed_password
        db.commit()
        
        logger.info(f"Password reset successfully for user: {normalized_phone}")
        return {"message": "Password reset successfully"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error resetting password with OTP: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to reset password: {str(e)}"
        )
