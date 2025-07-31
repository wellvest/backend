from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from typing import Dict, Any, List, Optional

from app.models.investment import Investment, InvestmentStatus
from app.models.wallet import IncomeWallet, IncomeTransaction, TransactionType, TransactionStatus
from app.utils.notification_utils import send_investment_return_notification

class InvestmentReturnService:
    @staticmethod
    async def calculate_returns(db: Session) -> Dict[str, Any]:
        """
        Calculate and apply returns for all active investments.
        This should be run on a schedule (e.g., daily).
        """
        active_investments = db.query(Investment).filter(
            Investment.status == InvestmentStatus.ACTIVE
        ).all()
        
        results = {
            "processed": 0,
            "total_returns_credited": 0.0,
            "details": []
        }
        
        for investment in active_investments:
            result = await InvestmentReturnService.process_investment_return(db, investment)
            if result:
                results["processed"] += 1
                results["total_returns_credited"] += result["amount_credited"]
                results["details"].append(result)
        
        return results
    
    @staticmethod
    async def process_investment_return(db: Session, investment: Investment) -> Optional[Dict[str, Any]]:
        """
        Process returns for a single investment.
        Returns information about the processed return or None if no action was taken.
        """
        # Skip if investment is not active
        if investment.status != InvestmentStatus.ACTIVE:
            return None
        
        # Calculate daily return based on the plan's interest rate
        # Annual interest rate / 365 = daily interest rate
        # For example, 12% annual interest = 0.12 / 365 = 0.00033 daily interest rate
        daily_interest_rate = investment.plan.interest_rate / 100 / 365
        daily_return = investment.amount * daily_interest_rate
        
        # Get or create income wallet
        wallet = db.query(IncomeWallet).filter(IncomeWallet.user_id == investment.user_id).first()
        if not wallet:
            wallet = IncomeWallet(user_id=investment.user_id)
            db.add(wallet)
            db.commit()
            db.refresh(wallet)
        
        # Create transaction for the return
        transaction = IncomeTransaction(
            wallet_id=wallet.id,
            amount=daily_return,
            transaction_type=TransactionType.CREDIT,
            status=TransactionStatus.COMPLETED,
            description=f"Daily return from {investment.plan_name} investment",
            reference_id=investment.id
        )
        db.add(transaction)
        
        # Update wallet balance
        wallet.balance += daily_return
        db.add(wallet)
        
        # Update investment returns total
        investment.returns += daily_return
        db.add(investment)
        
        # Check if investment period is over
        current_date = datetime.now()
        end_date = investment.start_date + timedelta(days=investment.duration_months * 30)
        
        if current_date >= end_date and investment.status == InvestmentStatus.ACTIVE:
            investment.status = InvestmentStatus.COMPLETED
            investment.end_date = current_date
            db.add(investment)
        
        db.commit()
        
        # Send notification to user about the return
        send_investment_return_notification(
            db=db,
            user_id=investment.user_id,
            plan_name=investment.plan_name,
            amount=daily_return
        )
        
        return {
            "investment_id": investment.id,
            "user_id": investment.user_id,
            "plan_name": investment.plan_name,
            "amount_credited": daily_return,
            "total_returns_to_date": investment.returns,
            "investment_status": investment.status
        }
    
    @staticmethod
    async def get_investment_summary(db: Session, user_id: str) -> Dict[str, Any]:
        """
        Get a summary of all investments and returns for a user.
        """
        investments = db.query(Investment).filter(Investment.user_id == user_id).all()
        
        active_investments = [inv for inv in investments if inv.status == InvestmentStatus.ACTIVE]
        completed_investments = [inv for inv in investments if inv.status == InvestmentStatus.COMPLETED]
        
        total_invested = sum(inv.amount for inv in investments)
        total_returns = sum(inv.returns for inv in investments)
        active_amount = sum(inv.amount for inv in active_investments)
        
        return {
            "total_investments": len(investments),
            "active_investments": len(active_investments),
            "completed_investments": len(completed_investments),
            "total_invested": total_invested,
            "total_returns": total_returns,
            "active_amount": active_amount,
            "roi_percentage": (total_returns / total_invested * 100) if total_invested > 0 else 0
        }
