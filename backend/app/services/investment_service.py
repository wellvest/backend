from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, timedelta
import calendar

from app.models.investment import Investment, InvestmentStatus
from app.models.wallet import IncomeWallet, IncomeTransaction, TransactionType, TransactionStatus
from app.services.wallet_service import WalletService
from app.services.notification_service import NotificationService

class InvestmentService:
    @staticmethod
    def get_user_investments(db: Session, user_id: str) -> List[Investment]:
        """
        Get all investments for a user.
        """
        return db.query(Investment).filter(
            Investment.user_id == user_id
        ).order_by(Investment.created_at.desc()).all()
    
    @staticmethod
    def get_active_investments(db: Session) -> List[Investment]:
        """
        Get all active investments.
        """
        return db.query(Investment).filter(
            Investment.status == InvestmentStatus.ACTIVE
        ).all()
    
    @staticmethod
    def calculate_monthly_interest(db: Session, investment_id: str) -> Optional[float]:
        """
        Calculate monthly interest for an investment.
        Fixed at 10% annual interest rate (0.833% monthly).
        """
        investment = db.query(Investment).filter(Investment.id == investment_id).first()
        if not investment or investment.status != InvestmentStatus.ACTIVE:
            return None
        
        # Use fixed 10% annual interest rate (0.833% monthly)
        monthly_interest_rate = 10.0 / 12 / 100  # Convert 10% annual to monthly decimal
        interest_amount = investment.amount * monthly_interest_rate
        
        return interest_amount
    
    @staticmethod
    def process_monthly_interest_payments(db: Session) -> int:
        """
        Process monthly interest payments for all active investments.
        Returns the number of payments processed.
        """
        # Get all active investments
        active_investments = InvestmentService.get_active_investments(db)
        payments_processed = 0
        
        for investment in active_investments:
            try:
                # Check if we should process interest for this investment
                if not InvestmentService._should_process_interest(investment):
                    continue
                
                # Calculate interest
                interest_amount = InvestmentService.calculate_monthly_interest(db, investment.id)
                if not interest_amount:
                    continue
                
                # Update investment returns
                investment.returns += interest_amount
                db.add(investment)
                
                # Add transaction to income wallet
                wallet = WalletService.get_or_create_income_wallet(db, investment.user_id)
                
                transaction = IncomeTransaction(
                    wallet_id=wallet.id,
                    amount=interest_amount,
                    transaction_type=TransactionType.CREDIT,
                    status=TransactionStatus.COMPLETED,
                    description=f"Monthly interest from {investment.plan_name} plan",
                    reference_id=investment.id
                )
                db.add(transaction)
                
                # Update wallet balance
                wallet.balance += interest_amount
                db.add(wallet)
                
                # Create notification
                NotificationService.create_interest_notification(
                    db=db,
                    user_id=investment.user_id,
                    investment_id=investment.id,
                    amount=interest_amount
                )
                
                payments_processed += 1
                
            except Exception as e:
                # Log error but continue processing other investments
                print(f"Error processing interest for investment {investment.id}: {str(e)}")
        
        # Commit all changes at once
        if payments_processed > 0:
            db.commit()
        
        return payments_processed
    
    @staticmethod
    def _should_process_interest(investment: Investment) -> bool:
        """
        Determine if we should process interest for this investment.
        Interest should be processed monthly from the start date.
        """
        today = datetime.now().date()
        start_date = investment.start_date.date()
        
        # If investment is less than a month old, check if it's the same day of month
        if (today.year == start_date.year and today.month == start_date.month):
            return False
        
        # Check if today is the same day of month as the start date
        # If start date is on a day that doesn't exist in current month (e.g., 31st),
        # then process on the last day of the current month
        day_to_process = min(start_date.day, calendar.monthrange(today.year, today.month)[1])
        
        return today.day == day_to_process
    
    @staticmethod
    def check_investment_completion(db: Session) -> int:
        """
        Check if any investments have reached their end date and mark them as completed.
        Returns the number of investments completed.
        """
        today = datetime.now().date()
        
        # Find investments that have reached their end date
        completed_investments = db.query(Investment).filter(
            Investment.status == InvestmentStatus.ACTIVE,
            Investment.end_date <= today
        ).all()
        
        for investment in completed_investments:
            investment.status = InvestmentStatus.COMPLETED
            db.add(investment)
            
            # Create notification
            NotificationService.create_investment_completed_notification(
                db=db,
                user_id=investment.user_id,
                investment_id=investment.id,
                amount=investment.amount,
                returns=investment.returns
            )
        
        if completed_investments:
            db.commit()
        
        return len(completed_investments)
