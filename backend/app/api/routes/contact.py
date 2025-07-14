from fastapi import APIRouter, HTTPException, BackgroundTasks, Body
from pydantic import BaseModel, EmailStr
from app.services.email_service import email_service

router = APIRouter()

class CallbackRequest(BaseModel):
    name: str
    phone: str
    service: str
    preferred_time: str
    message: str = None

class ContactMessage(BaseModel):
    full_name: str
    email: EmailStr
    phone: str = None
    subject: str
    message: str

# Email configuration
ADMIN_EMAIL = "wellvestltd@gmail.com"  # Recipient email

def send_email_background(subject: str, recipient: str, content: str):
    """Send email in the background using SendGrid"""
    print(f"\n\nAttempting to send email via SendGrid:")
    print(f"Subject: {subject}")
    print(f"Recipient: {recipient}")
    print(f"Content length: {len(content)} characters")
    
    try:
        print("Calling email_service.send_email...")
        result = email_service.send_email(
            to_email=recipient,
            subject=subject,
            html_content=content
        )
        print(f"SendGrid API response: {result}")
        
        if not result.get("success", False):
            print(f"Failed to send email: {result.get('error', 'Unknown error')}")
            return False
        print("Email sent successfully!")
        return True
    except Exception as e:
        print(f"Exception while sending email: {str(e)}")
        import traceback
        print(f"Traceback: {traceback.format_exc()}")
        return False

@router.post("/contact/callback", status_code=201)
async def request_callback(
    background_tasks: BackgroundTasks, 
    request: CallbackRequest = Body(...)
):
    """Endpoint to handle callback requests"""
    
    # Format email content
    subject = f"Callback Request from {request.name}"
    content = f"""
    <h2>New Callback Request</h2>
    <p><strong>Name:</strong> {request.name}</p>
    <p><strong>Phone:</strong> {request.phone}</p>
    <p><strong>Service:</strong> {request.service}</p>
    <p><strong>Preferred Time:</strong> {request.preferred_time}</p>
    """
    
    if request.message:
        content += f"<p><strong>Additional Message:</strong> {request.message}</p>"
    
    # Send email in background
    background_tasks.add_task(
        send_email_background,
        subject=subject,
        recipient=ADMIN_EMAIL,
        content=content
    )
    
    return {"message": "Callback request received successfully"}

@router.post("/contact/message", status_code=201)
async def send_contact_message(
    background_tasks: BackgroundTasks, 
    message: ContactMessage = Body(...)
):
    """Endpoint to handle contact form messages"""
    
    # Format email content
    subject = f"Contact Form: {message.subject}"
    content = f"""
    <h2>New Contact Message</h2>
    <p><strong>From:</strong> {message.full_name}</p>
    <p><strong>Email:</strong> {message.email}</p>
    """
    
    if message.phone:
        content += f"<p><strong>Phone:</strong> {message.phone}</p>"
    
    content += f"""
    <p><strong>Subject:</strong> {message.subject}</p>
    <p><strong>Message:</strong></p>
    <p>{message.message}</p>
    """
    
    # Send email in background
    background_tasks.add_task(
        send_email_background,
        subject=subject,
        recipient=ADMIN_EMAIL,
        content=content
    )
    
    return {"message": "Contact message sent successfully"}
