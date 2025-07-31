import os
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail, Email, To, Content, Subject
from typing import List, Optional
from pydantic import EmailStr
from app.core.config import settings

class EmailService:
    """Service for sending emails using SendGrid."""
    
    def __init__(self):
        self.api_key = os.environ.get('SENDGRID_API_KEY')
        self.from_email = os.environ.get('FROM_EMAIL', 'noreply@wellvest.com')
        self.admin_email = os.environ.get('ADMIN_EMAIL', 'admin@wellvest.com')
        
        # Debug info
        print(f"SendGrid API Key available: {bool(self.api_key)}")
        print(f"From Email: {self.from_email}")
        print(f"Admin Email: {self.admin_email}")
        print(f"API Key first 10 chars: {self.api_key[:10] if self.api_key else 'None'}...")
        
        try:
            self.sg_client = SendGridAPIClient(self.api_key)
            print("SendGrid client initialized successfully")
        except Exception as e:
            print(f"Error initializing SendGrid client: {str(e)}")
            raise
    
    def send_email(self, to_email: str, subject: str, html_content: str) -> dict:
        """Send an email using SendGrid."""
        message = Mail(
            from_email=self.from_email,
            to_emails=to_email,
            subject=subject,
            html_content=html_content
        )
        
        try:
            response = self.sg_client.send(message)
            return {
                "status_code": response.status_code,
                "body": response.body,
                "headers": response.headers,
                "success": True
            }
        except Exception as e:
            print(f"SendGrid Error: {str(e)}")
            import traceback
            print(f"Traceback: {traceback.format_exc()}")
            return {
                "error": str(e),
                "success": False
            }
    
    def send_welcome_email(self, user_email: str, user_name: str) -> dict:
        """Send welcome email to newly registered user."""
        subject = f"Welcome to Wellvest, {user_name}!"
        html_content = f"""
        <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px; border: 1px solid #eee; border-radius: 5px;">
            <h2 style="color: #4a6f8a;">Welcome to Wellvest!</h2>
            <p>Hello {user_name},</p>
            <p>Thank you for joining Wellvest. We're excited to have you on board!</p>
            <p>With your new Wellvest account, you can:</p>
            <ul>
                <li>Make smart investments</li>
                <li>Track your portfolio growth</li>
                <li>Refer friends and earn rewards</li>
                <li>Access exclusive investment opportunities</li>
            </ul>
            <p>To get started, please complete your KYC verification to unlock all features.</p>
            <p>If you have any questions, feel free to contact our support team.</p>
            <p>Best regards,<br>The Wellvest Team</p>
        </div>
        """
        
        return self.send_email(user_email, subject, html_content)
    
    def send_referral_notification(self, referrer_email: str, referrer_name: str, new_user_name: str) -> dict:
        """Send notification to a user when someone signs up using their referral code."""
        subject = "Congratulations! Someone joined using your referral"
        html_content = f"""
        <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px; border: 1px solid #eee; border-radius: 5px;">
            <h2 style="color: #4a6f8a;">Referral Success!</h2>
            <p>Hello {referrer_name},</p>
            <p>Great news! <strong>{new_user_name}</strong> has joined Wellvest using your referral code.</p>
            <p>Thank you for spreading the word about Wellvest. Your network is growing!</p>
            <p>Keep referring more friends to earn additional rewards and benefits.</p>
            <p>Best regards,<br>The Wellvest Team</p>
        </div>
        """
        
        return self.send_email(referrer_email, subject, html_content)
    
    def send_kyc_submission_notification(self, user_email: str, user_name: str) -> dict:
        """Send confirmation to user after KYC submission."""
        subject = "Your KYC Documents Have Been Submitted"
        html_content = f"""
        <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px; border: 1px solid #eee; border-radius: 5px;">
            <h2 style="color: #4a6f8a;">KYC Submission Received</h2>
            <p>Hello {user_name},</p>
            <p>We have received your KYC (Know Your Customer) documents. Our team will review them shortly.</p>
            <p>You will receive another email once your verification is complete.</p>
            <p>Thank you for your patience.</p>
            <p>Best regards,<br>The Wellvest Team</p>
        </div>
        """
        
        return self.send_email(user_email, subject, html_content)
    
    def notify_admin_of_kyc_submission(self, user_email: str, user_name: str, document_type: str) -> dict:
        """Notify admin about new KYC submission."""
        subject = f"New KYC Submission: {user_name}"
        html_content = f"""
        <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px; border: 1px solid #eee; border-radius: 5px;">
            <h2 style="color: #4a6f8a;">New KYC Submission</h2>
            <p>A new KYC submission has been received:</p>
            <ul>
                <li><strong>User:</strong> {user_name}</li>
                <li><strong>Email:</strong> {user_email}</li>
                <li><strong>Document Type:</strong> {document_type}</li>
            </ul>
            <p>Please review this submission in the admin dashboard.</p>
        </div>
        """
        
        return self.send_email(self.admin_email, subject, html_content)
    
    def send_kyc_verification_result(self, user_email: str, user_name: str, is_verified: bool) -> dict:
        """Send KYC verification result to user."""
        if is_verified:
            subject = "Your KYC Verification is Complete"
            html_content = f"""
            <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px; border: 1px solid #eee; border-radius: 5px;">
                <h2 style="color: #4a6f8a;">KYC Verification Approved</h2>
                <p>Hello {user_name},</p>
                <p>Great news! Your KYC verification has been approved.</p>
                <p>You now have full access to all Wellvest features and services.</p>
                <p>Thank you for your patience during this process.</p>
                <p>Best regards,<br>The Wellvest Team</p>
            </div>
            """
        else:
            subject = "Action Required: KYC Verification"
            html_content = f"""
            <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px; border: 1px solid #eee; border-radius: 5px;">
                <h2 style="color: #4a6f8a;">KYC Verification Update</h2>
                <p>Hello {user_name},</p>
                <p>We've reviewed your KYC documents and need additional information.</p>
                <p>Please log in to your account and resubmit your KYC documents with clearer images or additional details as required.</p>
                <p>If you have any questions, please contact our support team.</p>
                <p>Best regards,<br>The Wellvest Team</p>
            </div>
            """
        
        return self.send_email(user_email, subject, html_content)

# Create a singleton instance
email_service = EmailService()
