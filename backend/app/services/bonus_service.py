from sqlalchemy.orm import Session
from app.models.user import User
from app.models.wallet import IncomeWallet, IncomeTransaction, TransactionType, TransactionStatus
from app.models.network import Bonus
from typing import List, Dict, Any
import logging

logger = logging.getLogger(__name__)

class BonusService:
    """Service to handle bonus calculations and distributions"""
    
    @staticmethod
    async def process_referral_bonus(db: Session, user_id: str, plan_amount: float) -> Dict[str, Any]:
        """
        Process referral bonuses when a user buys a plan
        
        Args:
            db: Database session
            user_id: ID of the user who bought the plan
            plan_amount: Amount of the plan purchased
            
        Returns:
            Dictionary with bonus distribution details
        """
        result = {
            "success": True,
            "bonuses_distributed": [],
            "errors": []
        }
        
        try:
            # Get the user who bought the plan
            user = db.query(User).filter(User.id == user_id).first()
            if not user:
                result["success"] = False
                result["errors"].append(f"User with ID {user_id} not found")
                return result
                
            # Check if user has a referrer
            if not user.referrer_id:
                # No referrer, no bonus to distribute
                return result
                
            # Get the referrer chain (up to 3 levels)
            referrer_chain = BonusService._get_referrer_chain(db, user.referrer_id, max_depth=3)
            
            # Calculate and distribute bonuses based on level
            for level, referrer_id in enumerate(referrer_chain):
                bonus_percentage = BonusService._get_bonus_percentage(level)
                if bonus_percentage > 0:
                    bonus_amount = plan_amount * (bonus_percentage / 100)
                    
                    # Add bonus to referrer's wallet
                    success, message = await BonusService._add_bonus_to_wallet(
                        db, 
                        referrer_id, 
                        bonus_amount, 
                        f"Level {level+1} referral bonus from {user.name} ({user.member_id})",
                        user_id
                    )
                    
                    result["bonuses_distributed"].append({
                        "referrer_id": referrer_id,
                        "level": level + 1,
                        "percentage": bonus_percentage,
                        "amount": bonus_amount,
                        "success": success,
                        "message": message
                    })
                    
                    if not success:
                        result["errors"].append(message)
            
            return result
            
        except Exception as e:
            logger.error(f"Error processing referral bonus: {str(e)}")
            result["success"] = False
            result["errors"].append(f"Error processing referral bonus: {str(e)}")
            return result
    
    @staticmethod
    def _get_referrer_chain(db: Session, start_referrer_id: str, max_depth: int = 3) -> List[str]:
        """
        Get the chain of referrers starting from the given referrer ID
        
        Args:
            db: Database session
            start_referrer_id: ID of the first referrer
            max_depth: Maximum depth of the referrer chain
            
        Returns:
            List of referrer IDs in order (first element is direct referrer)
        """
        referrer_chain = []
        current_referrer_id = start_referrer_id
        depth = 0
        
        while current_referrer_id and depth < max_depth:
            referrer_chain.append(current_referrer_id)
            
            # Get the next referrer in the chain
            referrer = db.query(User).filter(User.id == current_referrer_id).first()
            if not referrer or not referrer.referrer_id:
                break
                
            current_referrer_id = referrer.referrer_id
            depth += 1
            
        return referrer_chain
    
    @staticmethod
    def _get_bonus_percentage(level: int) -> float:
        """
        Get the bonus percentage based on the referral level
        
        Args:
            level: Referral level (0 = direct referrer, 1 = referrer's referrer, etc.)
            
        Returns:
            Bonus percentage
        """
        if level == 0:
            return 4.0  # 4% for direct referrer
        elif level == 1:
            return 1.5  # 1.5% for level 2
        elif level == 2:
            return 0.5  # 0.5% for level 3
        else:
            return 0.0  # No bonus for higher levels
    
    @staticmethod
    async def _add_bonus_to_wallet(
        db: Session, 
        user_id: str, 
        amount: float, 
        description: str,
        reference_user_id: str
    ) -> tuple:
        """
        Add bonus amount to user's income wallet
        
        Args:
            db: Database session
            user_id: ID of the user receiving the bonus
            amount: Bonus amount
            description: Description of the bonus
            reference_user_id: ID of the user who triggered the bonus
            
        Returns:
            Tuple of (success: bool, message: str)
        """
        try:
            # Get or create income wallet
            wallet = db.query(IncomeWallet).filter(IncomeWallet.user_id == user_id).first()
            if not wallet:
                wallet = IncomeWallet(user_id=user_id, balance=0.0)
                db.add(wallet)
                db.flush()
            
            # Create bonus record
            bonus = Bonus(
                user_id=user_id,
                amount=amount,
                bonus_type="referral",
                description=description,
                reference_id=reference_user_id,
                is_paid=True
            )
            db.add(bonus)
            
            # Create transaction record
            transaction = IncomeTransaction(
                wallet_id=wallet.id,
                amount=amount,
                transaction_type=TransactionType.CREDIT,
                status=TransactionStatus.COMPLETED,
                description=description,
                reference_id=bonus.id
            )
            db.add(transaction)
            
            # Update wallet balance
            wallet.balance += amount
            db.add(wallet)
            
            db.commit()
            return True, f"Successfully added {amount} bonus to user {user_id}"
            
        except Exception as e:
            db.rollback()
            logger.error(f"Error adding bonus to wallet: {str(e)}")
            return False, f"Error adding bonus to wallet: {str(e)}"
