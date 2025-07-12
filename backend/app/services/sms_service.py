import os
import random
import string
import requests
import logging
from datetime import datetime, timedelta
from typing import Optional
from fastapi import HTTPException, status

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SMSService:
    def __init__(self):
        self.api_key = os.getenv("SMSMODE_API_KEY", "")
        self.base_url = "https://api.smsmode.com/http/1.6"
        self.sender = "WellVest"
        # Store OTPs with expiration time (in memory for now, should be moved to database in production)
        self.otps = {}  # {phone: {"otp": "123456", "expires_at": datetime}}
        
        # Development mode - if no API key or MOCK_SMS=true, use mock mode
        self.mock_mode = os.getenv("MOCK_SMS", "true").lower() == "true" or not self.api_key
        if self.mock_mode:
            logger.info("SMS Service running in MOCK MODE - no real SMS will be sent")
        else:
            logger.info(f"SMS Service initialized with API key: {self.api_key[:5]}...")

    def generate_otp(self, phone: str, length: int = 6) -> str:
        """Generate a random OTP and store it with expiration time"""
        otp = ''.join(random.choices(string.digits, k=length))
        # OTP expires in 10 minutes
        self.otps[phone] = {
            "otp": otp,
            "expires_at": datetime.now() + timedelta(minutes=10)
        }
        return otp

    def verify_otp(self, phone: str, otp: str) -> bool:
        """Verify if the provided OTP is valid and not expired"""
        if phone not in self.otps:
            return False
        
        stored_data = self.otps[phone]
        if stored_data["expires_at"] < datetime.now():
            # OTP expired, remove it
            del self.otps[phone]
            return False
        
        if stored_data["otp"] != otp:
            return False
        
        # OTP verified, remove it to prevent reuse
        del self.otps[phone]
        return True

    def send_sms(self, phone: str, message: str) -> bool:
        """Send SMS using SMS Mode API or mock in development"""
        # In mock mode, just log the message and return success
        if self.mock_mode:
            logger.info(f"MOCK SMS to {phone}: {message}")
            return True
            
        # Real SMS sending
        url = f"{self.base_url}/sendSMS.do"
        
        params = {
            "accessToken": self.api_key,
            "message": message,
            "numero": phone,
            "emetteur": self.sender
        }
        
        try:
            logger.info(f"Sending SMS to {phone}")
            response = requests.get(url, params=params)
            response_data = response.text
            logger.info(f"SMS API response: {response_data}")
            
            # SMS Mode API returns a response code at the beginning of the response
            if response_data.startswith("0"):
                logger.info(f"SMS sent successfully to {phone}")
                return True
            else:
                error_code = response_data.split("|")[0] if "|" in response_data else response_data
                error_msg = f"Failed to send SMS. Error code: {error_code}"
                logger.error(error_msg)
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=error_msg
                )
        except Exception as e:
            error_msg = f"SMS service error: {str(e)}"
            logger.error(error_msg)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=error_msg
            )

    def send_otp(self, phone: str, purpose: str = "verification") -> str:
        """Generate and send OTP to the user's phone"""
        # Normalize phone number - remove spaces and ensure it starts with +
        phone = phone.strip().replace(" ", "")
        if not phone.startswith("+"):
            phone = "+" + phone
            
        otp = self.generate_otp(phone)
        logger.info(f"Generated OTP for {phone} (purpose: {purpose}): {otp}")
        
        if purpose == "signup":
            message = f"Your WellVest signup verification code is: {otp}. Valid for 10 minutes."
        elif purpose == "reset_password":
            message = f"Your WellVest password reset code is: {otp}. Valid for 10 minutes."
        else:
            message = f"Your WellVest verification code is: {otp}. Valid for 10 minutes."
        
        self.send_sms(phone, message)
        return otp

# Create a singleton instance
sms_service = SMSService()
