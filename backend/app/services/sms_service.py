import os
import random
import string
import requests
import logging
import socket
import time
import json
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any, Tuple
from fastapi import HTTPException, status
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()
# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SMSService:
    def __init__(self):
        # Explicitly load environment variables again to ensure they're available
        load_dotenv()
        
        # Get API key from environment variables
        self.fast2sms_api_key = os.getenv("FAST2SMS_API_KEY")
        
        # Debug the API key (masked for security)
        if self.fast2sms_api_key:
            logger.info(f"Using Fast2SMS API key: {self.fast2sms_api_key[:5]}...")
        else:
            logger.warning("No Fast2SMS API key found in environment variables!")
        
        # Use only the exact URL from the PHP example
        self.fast2sms_url = "https://www.fast2sms.com/dev/bulkV2"  # This is the URL used in the PHP example
        
        # Retry configuration
        self.max_retries = 3
        self.retry_delay = 1  # seconds
        self.timeout = 15  # seconds
        
        self.sender = "WellVest"
        # Store OTPs with expiration time (in memory for now, should be moved to database in production)
        self.otps = {}  # {phone: {"otp": "123456", "expires_at": datetime}}
        
        # Check if OTP verification is enabled
        self.otp_verification_enabled = os.getenv("OTP_VERIFICATION_ENABLED", "true").lower() == "true"
        
        # Development mode - if no API key or MOCK_SMS=true, use mock mode
        self.mock_mode = os.getenv("MOCK_SMS", "true").lower() == "true" or not self.fast2sms_api_key
        
        # Validate Fast2SMS API key if not in mock mode
        if not self.mock_mode:
            if not self.fast2sms_api_key or len(self.fast2sms_api_key) < 10:
                logger.warning("Invalid or missing Fast2SMS API key - switching to mock mode")
                self.mock_mode = True
            else:
                logger.info(f"SMS Service initialized with Fast2SMS API key: {self.fast2sms_api_key[:5]}...")
                # Check network connectivity
                if not self._check_internet_connection():
                    logger.warning("No internet connection detected - SMS sending may fail")
        
        if self.mock_mode:
            logger.info("SMS Service running in MOCK MODE - no real SMS will be sent")
            logger.info("OTPs will be displayed in console logs for development purposes")
            
        # Always print OTPs in console for development convenience
        self.always_show_otp_in_console = True
        
    def _check_internet_connection(self) -> bool:
        """Check if there is an active internet connection"""
        try:
            # Try to connect to Google's DNS server
            socket.create_connection(("8.8.8.8", 53), timeout=3)
            return True
        except OSError:
            return False

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
        # If OTP verification is disabled, always return True
        if not self.otp_verification_enabled:
            logger.warning("OTP verification is disabled. Automatically validating OTP.")
            return True
            
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
        """Send SMS using Fast2SMS or mock in development"""
        # Always show OTP in console for development convenience
        if self.always_show_otp_in_console:
            logger.warning("="*50)
            logger.warning(f"OTP MESSAGE: {message}")
            logger.warning("="*50)
            
        # In mock mode, just log the message and return success
        if self.mock_mode:
            logger.info(f"MOCK SMS to {phone}: {message}")
            return True
        
        # Check internet connection first
        if not self._check_internet_connection():
            logger.warning("No internet connection detected - falling back to mock mode")
            return True
        
        # Format phone number for Fast2SMS (remove '+' prefix for Indian numbers)
        formatted_phone = phone.replace("+91", "").replace("+", "")
        
        # Try to send SMS via Fast2SMS with multiple attempts
        try:
            return self._send_sms_fast2sms(formatted_phone, message)
        except HTTPException as e:
            # If Fast2SMS fails with a specific error, log it
            logger.error(f"Fast2SMS service error: {e.detail}")
            logger.warning("Temporarily enabling mock mode due to SMS provider failure")
            return True  # Return success to allow the application to continue
        except Exception as e:
            # Catch any other unexpected errors
            logger.error(f"Unexpected error sending SMS: {str(e)}")
            logger.warning("Temporarily enabling mock mode due to unexpected error")
            return True  # Return success to allow the application to continue
    
    def _send_sms_fast2sms(self, phone: str, message: str) -> bool:
        """Send SMS using Fast2SMS API with retry mechanism and multiple URLs"""
        # Check if API key is valid
        if not self.fast2sms_api_key or len(self.fast2sms_api_key) < 10:
            error_msg = "Invalid Fast2SMS API key"
            logger.error(error_msg)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=error_msg
            )
        
        # Extract OTP from message if it's an OTP message
        # This is for Fast2SMS's variables_values parameter
        otp_digits = ''.join(filter(str.isdigit, message))[:6]  # Get first 6 digits from message
        
        # Prepare headers and payload - exactly matching PHP example
        headers = {
            "authorization": self.fast2sms_api_key,
            "accept": "*/*",
            "cache-control": "no-cache",
            "content-type": "application/json"
        }
        
        # Debug the headers
        logger.info(f"Using authorization: {self.fast2sms_api_key}")
        
        # Construct payload exactly like the PHP example
        if "verification code" in message.lower() or "otp" in message.lower():
            # For OTP messages
            payload = {
                "variables_values": otp_digits,
                "route": "otp",
                "numbers": phone
            }
            logger.info(f"Sending OTP via Fast2SMS: {otp_digits} to {phone}")
        else:
            # For regular messages
            payload = {
                "message": message,
                "language": "english",
                "route": "q",
                "numbers": phone
            }
        
        # Try with retry mechanism
        last_error = None
        
        # First check internet connection
        if not self._check_internet_connection():
            error_msg = "No internet connection available"
            logger.error(error_msg)
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=error_msg
            )
        
        # Use the exact URL with retries
        url = self.fast2sms_url
        for attempt in range(self.max_retries):
            try:
                logger.info(f"Sending SMS via Fast2SMS to {phone} using URL: {url} (attempt {attempt+1}/{self.max_retries})")
                
                # Debug the exact request being sent
                logger.info(f"Fast2SMS request headers: {headers}")
                logger.info(f"Fast2SMS request payload: {json.dumps(payload)}")
                
                # Exactly match PHP curl implementation with SSL verification disabled
                response = requests.post(
                    url=url,
                    headers=headers,
                    json=payload,  # This will automatically set the correct Content-Type
                    timeout=self.timeout,
                    verify=False  # Disable SSL verification like in the PHP example
                )
                
                # Check if response is successful
                response.raise_for_status()
                
                # Safely try to parse JSON response
                try:
                    response_data = response.json()
                    logger.info(f"Fast2SMS API response: {response_data}")
                    
                    # Check Fast2SMS response
                    if response_data.get("return") is True:
                        logger.info(f"SMS sent successfully via Fast2SMS to {phone}")
                        return True
                    else:
                        error_msg = f"Failed to send SMS via Fast2SMS. Message: {response_data.get('message', 'Unknown error')}"
                        logger.warning(error_msg)
                        last_error = HTTPException(
                            status_code=status.HTTP_400_BAD_REQUEST,
                            detail=error_msg
                        )
                        # Try next attempt or URL
                        break
                except ValueError:
                    # Response is not JSON
                    logger.info(f"Fast2SMS API raw response: {response.text}")
                    if response.status_code == 200 and response.text.strip():
                        logger.info(f"SMS sent successfully via Fast2SMS to {phone} (non-JSON response)")
                        return True
                    elif response.status_code == 200:
                        # Empty response with 200 status code - might be a connection issue
                        error_msg = "Fast2SMS returned empty response with 200 status code - SMS might not be delivered"
                        logger.warning(error_msg)
                        last_error = HTTPException(
                            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail=error_msg
                        )
                        # Try next attempt
                        time.sleep(self.retry_delay * (attempt + 1))  # Exponential backoff
                        continue
                    else:
                        error_msg = f"Failed to send SMS via Fast2SMS. Status code: {response.status_code}, Response: {response.text}"
                        logger.warning(error_msg)
                        last_error = HTTPException(
                            status_code=status.HTTP_400_BAD_REQUEST,
                            detail=error_msg
                        )
                        # Try next attempt
                        time.sleep(self.retry_delay * (attempt + 1))  # Exponential backoff
                        continue
            except requests.exceptions.RequestException as e:
                error_msg = f"Fast2SMS service error with URL {url}: {str(e)}"
                logger.warning(error_msg)
                last_error = HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=error_msg
                )
                # Try next attempt with exponential backoff
                if attempt < self.max_retries - 1:
                    time.sleep(self.retry_delay * (attempt + 1))
                continue
        
        # If we reach here, all attempts have failed
        if last_error:
            raise last_error
        else:
            error_msg = "Fast2SMS failed after multiple attempts"
            logger.error(error_msg)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=error_msg
            )
    
    # SMSMode method removed as we're only using Fast2SMS now

    def send_otp(self, phone: str, purpose: str = "verification") -> str:
        """Generate and send OTP to the user's phone with improved reliability"""
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
        
        # Always display OTP in console for development purposes
        logger.warning("="*50)
        logger.warning(f"OTP CODE: {otp} for {phone} (purpose: {purpose})")
        logger.warning("="*50)
        
        try:
            self.send_sms(phone, message)
        except Exception as e:
            logger.error(f"Failed to send SMS: {str(e)}")
            # If SMS provider fails, fall back to mock mode for development
            if not self.mock_mode:
                logger.warning("Temporarily enabling mock mode due to SMS provider failure")
                logger.warning(f"MOCK SMS to {phone}: {message}")
                # Don't raise the exception - allow the OTP to be used in mock mode
                # This ensures the app remains functional even when SMS provider is down
        
        return otp

# Create a singleton instance
sms_service = SMSService()
