from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Dict, Any
from datetime import datetime, timedelta

from app.db.database import get_db
from app.core.auth import get_current_active_user
from app.utils.notification_utils import send_bonus_credited_notification
from app.models.network import Bonus

router = APIRouter()

@router.get("/bonuses", response_model=List[Dict[str, Any]])
def get_bonuses(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_active_user),
):
    """
    Get all bonuses for the current user
    """
    bonuses = db.query(Bonus).filter(Bonus.user_id == current_user.id).all()
    return [bonus.__dict__ for bonus in bonuses]

@router.get("/bonuses/summary", response_model=Dict[str, Any])
def get_bonus_summary(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_active_user),
):
    """
    Get a summary of bonuses for the current user
    """
    # Get all bonuses for the user
    bonuses = db.query(Bonus).filter(Bonus.user_id == current_user.id).all()
    
    # Calculate total bonus amount
    total_bonus = sum(bonus.amount for bonus in bonuses)
    
    # Calculate monthly bonus (last 30 days)
    thirty_days_ago = datetime.now() - timedelta(days=30)
    monthly_bonuses = [b for b in bonuses if b.created_at >= thirty_days_ago]
    monthly_bonus = sum(bonus.amount for bonus in monthly_bonuses)
    
    # Calculate pending bonuses (not paid)
    pending_bonuses = [b for b in bonuses if not b.is_paid]
    pending_amount = sum(bonus.amount for bonus in pending_bonuses)
    
    # Calculate paid bonuses
    paid_bonuses = [b for b in bonuses if b.is_paid]
    paid_amount = sum(bonus.amount for bonus in paid_bonuses)
    
    return {
        "total_bonus": total_bonus,
        "monthly_bonus": monthly_bonus,
        "pending_amount": pending_amount,
        "paid_amount": paid_amount,
        "bonus_count": len(bonuses),
    }

@router.get("/bonuses/history", response_model=List[Dict[str, Any]])
def get_bonus_history(
    skip: int = 0,
    limit: int = 20,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_active_user),
):
    """
    Get paginated bonus history for the current user
    """
    bonuses = db.query(Bonus).filter(
        Bonus.user_id == current_user.id
    ).order_by(Bonus.created_at.desc()).offset(skip).limit(limit).all()
    
    return [{
        "id": str(bonus.id),
        "amount": bonus.amount,
        "bonus_type": bonus.bonus_type,
        "is_paid": bonus.is_paid,
        "created_at": bonus.created_at,
        "paid_at": bonus.paid_at
    } for bonus in bonuses]

@router.get("/bonuses/network-earnings", response_model=Dict[str, Any])
def get_network_earnings(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_active_user),
):
    """
    Get network earnings breakdown for the current user
    """
    # Get all bonuses for the user
    bonuses = db.query(Bonus).filter(Bonus.user_id == current_user.id).all()
    
    # Group bonuses by type
    bonus_by_type = {}
    for bonus in bonuses:
        if bonus.bonus_type not in bonus_by_type:
            bonus_by_type[bonus.bonus_type] = 0
        bonus_by_type[bonus.bonus_type] += bonus.amount
    
    # Calculate total network earnings
    total_earnings = sum(bonus.amount for bonus in bonuses)
    
    return {
        "total_earnings": total_earnings,
        "breakdown_by_type": bonus_by_type,
        "recent_earnings": [{
            "id": str(bonus.id),
            "amount": bonus.amount,
            "bonus_type": bonus.bonus_type,
            "created_at": bonus.created_at
        } for bonus in sorted(bonuses, key=lambda x: x.created_at, reverse=True)[:5]]
    }
