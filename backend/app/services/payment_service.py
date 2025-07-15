from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime

from app.models.payment import Payment, PaymentStatus
from app.models.investment import Investment, InvestmentStatus
from app.models.user import Profile
from app.schemas.payment import PaymentCreate, PaymentUpdate
from app.services.notification_service import NotificationService

class PaymentService:
    @staticmethod
    def get_payments(db: Session, skip: int = 0, limit: int = 100) -> List[Payment]:
        """
        Retrieve all payments with pagination.
        """
        return db.query(Payment).order_by(Payment.created_at.desc()).offset(skip).limit(limit).all()
    
    @staticmethod
    def get_user_payments(db: Session, user_id: str, skip: int = 0, limit: int = 100) -> List[Payment]:
        """
        Retrieve payments for a specific user with pagination.
        """
        return db.query(Payment).filter(Payment.user_id == user_id).order_by(Payment.created_at.desc()).offset(skip).limit(limit).all()
    
    @staticmethod
    def get_payment_by_id(db: Session, payment_id: str) -> Optional[Payment]:
        """
        Get a specific payment by ID.
        """
        return db.query(Payment).filter(Payment.id == payment_id).first()
    
    @staticmethod
    def create_payment(db: Session, payment_data: PaymentCreate) -> Payment:
        """
        Create a new payment.
        """
        db_payment = Payment(
            user_id=payment_data.user_id,
            plan_id=payment_data.plan_id,
            amount=payment_data.amount,
            upi_ref_id=payment_data.upi_ref_id,
            status=PaymentStatus.PENDING,
        )
        db.add(db_payment)
        db.commit()
        db.refresh(db_payment)
        
        # Create notification for user
        NotificationService.create_payment_notification(
            db=db,
            user_id=payment_data.user_id,
            payment_id=db_payment.id,
            amount=payment_data.amount
        )
        
        return db_payment
    
    @staticmethod
    def update_payment(db: Session, payment_id: str, payment_data: PaymentUpdate) -> Optional[Payment]:
        """
        Update an existing payment.
        """
        db_payment = PaymentService.get_payment_by_id(db, payment_id)
        if not db_payment:
            return None
        
        update_data = payment_data.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_payment, field, value)
        
        db.add(db_payment)
        db.commit()
        db.refresh(db_payment)
        return db_payment
    
    @staticmethod
    def approve_payment(db: Session, payment_id: str, admin_notes: Optional[str] = None) -> Optional[Payment]:
        """
        Approve a payment and create the corresponding investment.
        """
        db_payment = PaymentService.get_payment_by_id(db, payment_id)
        if not db_payment or db_payment.status != PaymentStatus.PENDING:
            return None
        
        # Update payment status
        db_payment.status = PaymentStatus.APPROVED
        if admin_notes:
            db_payment.admin_notes = admin_notes
        
        db.add(db_payment)
        db.commit()
        db.refresh(db_payment)
        
        # Get plan details
        plan = db_payment.plan
        if not plan:
            raise ValueError(f"Plan with ID {db_payment.plan_id} not found")
        
        # Calculate end date based on plan duration
        from datetime import datetime, timedelta
        start_date = datetime.now()
        end_date = start_date + timedelta(days=30 * plan.duration_months)
        
        # Create investment
        from app.models.investment import Investment, InvestmentStatus
        db_investment = Investment(
            user_id=db_payment.user_id,
            plan_id=db_payment.plan_id,
            plan_name=plan.name,
            amount=db_payment.amount,
            duration_months=plan.duration_months,
            start_date=start_date,
            end_date=end_date,
            status=InvestmentStatus.ACTIVE,
            returns=0.0  # Initial returns are zero
        )
        db.add(db_investment)
        db.flush()  # Flush to get the investment ID
        
        # Update user profile with current plan
        user_profile = db.query(Profile).filter(Profile.user_id == db_payment.user_id).first()
        if user_profile:
            user_profile.current_plan_id = db_payment.plan_id
            user_profile.plan_amount = db_payment.amount
            db.add(user_profile)
        else:
            # Create profile if it doesn't exist
            from app.models.user import Profile
            new_profile = Profile(
                user_id=db_payment.user_id,
                current_plan_id=db_payment.plan_id,
                plan_amount=db_payment.amount
            )
            db.add(new_profile)
        
        # Process team investments if applicable
        try:
            from app.services.network_service import NetworkService
            NetworkService.process_team_investment(db, db_investment.id)
        except Exception as e:
            # Log the error but continue with the payment approval
            print(f"Error processing team investment: {str(e)}")
        
        db.commit()
        
        # Create notification for user
        try:
            NotificationService.create_payment_approved_notification(
                db=db,
                user_id=db_payment.user_id,
                payment_id=db_payment.id,
                amount=db_payment.amount
            )
        except Exception as e:
            # Log the error but continue with the payment approval
            print(f"Error creating notification: {str(e)}")
        
        return db_payment
    
    @staticmethod
    def reject_payment(db: Session, payment_id: str, admin_notes: Optional[str] = None) -> Optional[Payment]:
        """
        Reject a payment.
        """
        db_payment = PaymentService.get_payment_by_id(db, payment_id)
        if not db_payment or db_payment.status != PaymentStatus.PENDING:
            return None
        
        # Update payment status
        db_payment.status = PaymentStatus.REJECTED
        if admin_notes:
            db_payment.admin_notes = admin_notes
        
        db.add(db_payment)
        db.commit()
        db.refresh(db_payment)
        
        # Create notification for user
        NotificationService.create_payment_rejected_notification(
            db=db,
            user_id=db_payment.user_id,
            payment_id=db_payment.id,
            amount=db_payment.amount,
            reason=admin_notes or "No reason provided"
        )
        
        return db_payment
    
    @staticmethod
    def get_pending_payments(db: Session, skip: int = 0, limit: int = 100) -> List[Payment]:
        """
        Get all pending payments for admin approval.
        """
        return db.query(Payment).filter(Payment.status == PaymentStatus.PENDING).order_by(Payment.created_at).offset(skip).limit(limit).all()
