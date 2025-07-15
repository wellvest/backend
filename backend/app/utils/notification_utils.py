from typing import Optional
from sqlalchemy.orm import Session
from app.services.notification_service import NotificationService
from app.models.user import User


def send_plan_selection_notification(db: Session, user_id: str, plan_name: str, amount: float) -> None:
    """
    Send a notification to the user when they select a new investment plan
    """
    notification_service = NotificationService(db)
    notification_service.create_system_notification(
        user_id=user_id,
        title="Investment Plan Selected",
        message=f"You have successfully selected the {plan_name} investment plan for ₹{amount:,.0f}.",
        notification_type="success"
    )


def send_plan_activation_notification(db: Session, user_id: str, plan_name: str) -> None:
    """
    Send a notification to the user when their investment plan is activated
    """
    notification_service = NotificationService(db)
    notification_service.create_system_notification(
        user_id=user_id,
        title="Plan Activated",
        message=f"Your {plan_name} investment plan has been activated successfully.",
        notification_type="success"
    )


def send_team_member_joined_notification(db: Session, team_leader_id: str, member_name: str) -> None:
    """
    Send a notification to the team leader when a new member joins their team
    """
    notification_service = NotificationService(db)
    notification_service.create_system_notification(
        user_id=team_leader_id,
        title="New Team Member",
        message=f"{member_name} has joined your team plan.",
        notification_type="info"
    )


def send_bonus_credited_notification(db: Session, user_id: str, amount: float, bonus_type: str) -> None:
    """
    Send a notification to the user when a bonus is credited to their account
    """
    notification_service = NotificationService(db)
    notification_service.create_system_notification(
        user_id=user_id,
        title="Bonus Credited",
        message=f"₹{amount:,.0f} {bonus_type} bonus has been credited to your account.",
        notification_type="success"
    )


def send_kyc_verification_notification(db: Session, user_id: str, status: str) -> None:
    """
    Send a notification to the user about their KYC verification status
    """
    notification_service = NotificationService(db)
    
    if status.lower() == "approved":
        notification_service.create_system_notification(
            user_id=user_id,
            title="KYC Verification Approved",
            message="Your KYC documents have been verified successfully.",
            notification_type="success"
        )
    elif status.lower() == "rejected":
        notification_service.create_system_notification(
            user_id=user_id,
            title="KYC Verification Failed",
            message="Your KYC verification was unsuccessful. Please check your documents and try again.",
            notification_type="warning"
        )
    else:
        notification_service.create_system_notification(
            user_id=user_id,
            title="KYC Verification Update",
            message=f"Your KYC verification status: {status}.",
            notification_type="info"
        )


def send_address_verification_notification(db: Session, user_id: str) -> None:
    """
    Send a notification to the user when their address needs verification
    """
    notification_service = NotificationService(db)
    notification_service.create_system_notification(
        user_id=user_id,
        title="Address Verification Required",
        message="Please complete your address verification to continue using all features.",
        notification_type="warning"
    )


def send_voucher_notification(db: Session, user_id: str, voucher_code: str, expiry_days: int) -> None:
    """
    Send a notification to the user about a new voucher
    """
    notification_service = NotificationService(db)
    notification_service.create_system_notification(
        user_id=user_id,
        title="Shopping Voucher Received",
        message=f"You've received a shopping voucher code: {voucher_code}. Valid for {expiry_days} days.",
        notification_type="info"
    )


def send_voucher_expiry_notification(db: Session, user_id: str, voucher_code: str, days_left: int) -> None:
    """
    Send a notification to the user about a voucher that's about to expire
    """
    notification_service = NotificationService(db)
    notification_service.create_system_notification(
        user_id=user_id,
        title="Voucher Expiring Soon",
        message=f"Your shopping voucher {voucher_code} will expire in {days_left} days.",
        notification_type="warning"
    )


def send_password_reset_notification(db: Session, user_id: str) -> None:
    """
    Send a notification to the user when their password is reset
    """
    notification_service = NotificationService(db)
    notification_service.create_system_notification(
        user_id=user_id,
        title="Password Reset",
        message="Your password has been reset successfully.",
        notification_type="info"
    )


def send_welcome_notification(db: Session, user_id: str, user_name: str) -> None:
    """
    Send a welcome notification to a new user
    """
    notification_service = NotificationService(db)
    notification_service.create_system_notification(
        user_id=user_id,
        title="Welcome to WellVest",
        message=f"Welcome to WellVest, {user_name}! We're excited to have you on board.",
        notification_type="success"
    )


def send_phone_verification_notification(db: Session, user_id: str) -> None:
    """
    Send a notification to the user when their phone number is verified
    """
    notification_service = NotificationService(db)
    notification_service.create_system_notification(
        user_id=user_id,
        title="Phone Verified",
        message="Your phone number has been successfully verified.",
        notification_type="success"
    )


def send_payment_notification(db: Session, user_id: str, payment_id: str, amount: float) -> None:
    """
    Send a notification to the user when they submit a payment
    """
    notification_service = NotificationService(db)
    notification_service.create_system_notification(
        user_id=user_id,
        title="Payment Submitted",
        message=f"Your payment of ₹{amount:,.0f} has been submitted and is pending approval.",
        notification_type="info"
    )


def send_payment_approved_notification(db: Session, user_id: str, payment_id: str, amount: float) -> None:
    """
    Send a notification to the user when their payment is approved
    """
    notification_service = NotificationService(db)
    notification_service.create_system_notification(
        user_id=user_id,
        title="Payment Approved",
        message=f"Your payment of ₹{amount:,.0f} has been approved. Your investment plan is now active.",
        notification_type="success"
    )


def send_payment_rejected_notification(db: Session, user_id: str, payment_id: str, amount: float, reason: str) -> None:
    """
    Send a notification to the user when their payment is rejected
    """
    notification_service = NotificationService(db)
    notification_service.create_system_notification(
        user_id=user_id,
        title="Payment Rejected",
        message=f"Your payment of ₹{amount:,.0f} has been rejected. Reason: {reason}",
        notification_type="warning"
    )


def send_investment_return_notification(db: Session, user_id: str, plan_name: str, amount: float) -> None:
    """
    Send a notification to the user when their investment generates a return
    """
    notification_service = NotificationService(db)
    notification_service.create_system_notification(
        user_id=user_id,
        title="Investment Return Credited",
        message=f"₹{amount:,.2f} has been credited to your income wallet from your {plan_name} investment.",
        notification_type="success"
    )


def send_team_investment_notification(db: Session, user_id: str, amount: float, level: int, team_member_name: str) -> None:
    """
    Send a notification to the user when they receive a team investment commission
    """
    notification_service = NotificationService(db)
    notification_service.create_system_notification(
        user_id=user_id,
        title="Team Commission Earned",
        message=f"₹{amount:,.2f} has been credited to your income wallet as a level {level} commission from {team_member_name}'s investment.",
        notification_type="success"
    )
