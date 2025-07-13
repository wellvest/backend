from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Dict, Any
from sqlalchemy import desc, func
from pydantic import BaseModel

from app.core.auth import get_current_active_user, get_current_active_superuser
from app.db.database import get_db
from app.models.user import User
from app.models.network import Bonus
from app.models.wallet import IncomeWallet, IncomeTransaction
from app.utils.notification_utils import send_bonus_credited_notification

router = APIRouter()

@router.get("/bonus/summary", response_model=Dict[str, Any])
async def get_bonus_summary(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get bonus summary for the current user."""
    # Get user's income wallet
    wallet = db.query(IncomeWallet).filter(IncomeWallet.user_id == current_user.id).first()
    if not wallet:
        wallet = IncomeWallet(user_id=current_user.id, balance=0.0)
        db.add(wallet)
        db.commit()
        db.refresh(wallet)
    
    # Get total bonus amount
    total_bonus = db.query(Bonus).filter(
        Bonus.user_id == current_user.id,
        Bonus.is_paid == True
    ).with_entities(
        func.sum(Bonus.amount).label("total")
    ).scalar() or 0.0
    
    # Get recent bonuses
    recent_bonuses = db.query(Bonus).filter(
        Bonus.user_id == current_user.id
    ).order_by(desc(Bonus.created_at)).limit(5).all()
    
    # Format recent bonuses
    formatted_bonuses = []
    for bonus in recent_bonuses:
        # Get referrer information if available
        referrer_name = "System"
        referrer_id = ""
        if bonus.reference_id:
            referrer = db.query(User).filter(User.id == bonus.reference_id).first()
            if referrer:
                referrer_name = referrer.name
                referrer_id = referrer.member_id or ""
        
        formatted_bonuses.append({
            "id": bonus.id,
            "amount": bonus.amount,
            "bonus_type": bonus.bonus_type,
            "description": bonus.description,
            "created_at": bonus.created_at,
            "referrer_name": referrer_name,
            "referrer_id": referrer_id,
            "is_paid": bonus.is_paid
        })
    
    # Calculate TDS (assuming 6.5% TDS)
    tds_percentage = 6.5
    tds_amount = total_bonus * (tds_percentage / 100)
    net_amount = total_bonus - tds_amount
    
    return {
        "total_bonus": total_bonus,
        "tds_percentage": tds_percentage,
        "tds_amount": tds_amount,
        "net_amount": net_amount,
        "wallet_balance": wallet.balance,
        "recent_bonuses": formatted_bonuses
    }

@router.get("/bonus/history", response_model=List[Dict[str, Any]])
async def get_bonus_history(
    skip: int = 0,
    limit: int = 20,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get bonus history for the current user."""
    # Get all bonuses
    bonuses = db.query(Bonus).filter(
        Bonus.user_id == current_user.id
    ).order_by(desc(Bonus.created_at)).offset(skip).limit(limit).all()
    
    # Format bonuses
    formatted_bonuses = []
    for bonus in bonuses:
        # Get referrer information if available
        referrer_name = "System"
        referrer_id = ""
        referrer_avatar = ""
        if bonus.reference_id:
            referrer = db.query(User).filter(User.id == bonus.reference_id).first()
            if referrer:
                referrer_name = referrer.name
                referrer_id = referrer.member_id or ""
                referrer_avatar = referrer.avatar or ""
        
        formatted_bonuses.append({
            "id": bonus.id,
            "amount": bonus.amount,
            "bonus_type": bonus.bonus_type,
            "description": bonus.description,
            "created_at": bonus.created_at,
            "referrer_name": referrer_name,
            "referrer_id": referrer_id,
            "referrer_avatar": referrer_avatar,
            "is_paid": bonus.is_paid
        })
    
    return formatted_bonuses

@router.get("/bonus/network-earnings", response_model=Dict[str, Any])
async def get_network_earnings(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get earnings from network referrals."""
    # Get all direct referrals
    direct_referrals = db.query(User).filter(User.referrer_id == current_user.id).all()
    
    # Calculate earnings from each level
    level_earnings = {
        "level1": 0.0,  # Direct referrals (4%)
        "level2": 0.0,  # Referrals of referrals (1.5%)
        "level3": 0.0   # Referrals of referrals of referrals (0.5%)
    }
    
    # Get bonuses by reference_id to calculate earnings by level
    for referral in direct_referrals:
        # Level 1 (direct referrals)
        level1_bonuses = db.query(Bonus).filter(
            Bonus.user_id == current_user.id,
            Bonus.reference_id == referral.id
        ).with_entities(
            func.sum(Bonus.amount).label("total")
        ).scalar() or 0.0
        
        level_earnings["level1"] += level1_bonuses
        
        # Get referrals of this referral (level 2)
        level2_referrals = db.query(User).filter(User.referrer_id == referral.id).all()
        for level2_referral in level2_referrals:
            level2_bonuses = db.query(Bonus).filter(
                Bonus.user_id == current_user.id,
                Bonus.reference_id == level2_referral.id
            ).with_entities(
                func.sum(Bonus.amount).label("total")
            ).scalar() or 0.0
            
            level_earnings["level2"] += level2_bonuses
            
            # Get referrals of level 2 referrals (level 3)
            level3_referrals = db.query(User).filter(User.referrer_id == level2_referral.id).all()
            for level3_referral in level3_referrals:
                level3_bonuses = db.query(Bonus).filter(
                    Bonus.user_id == current_user.id,
                    Bonus.reference_id == level3_referral.id
                ).with_entities(
                    func.sum(Bonus.amount).label("total")
                ).scalar() or 0.0
                
                level_earnings["level3"] += level3_bonuses
    
    # Calculate total earnings
    total_earnings = sum(level_earnings.values())
    
    return {
        "total_earnings": total_earnings,
        "level_earnings": level_earnings,
        "direct_referrals_count": len(direct_referrals)
    }


class BonusCreditRequest(BaseModel):
    user_id: str
    amount: float
    bonus_type: str
    description: str
    reference_id: str = None


@router.post("/bonus/credit", response_model=Dict[str, Any], status_code=status.HTTP_201_CREATED)
async def credit_bonus(
    bonus_in: BonusCreditRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_superuser)  # Only admins can credit bonuses
):
    """Credit a bonus to a user's account and send a notification."""
    # Verify user exists
    user = db.query(User).filter(User.id == bonus_in.user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Create bonus record
    bonus = Bonus(
        user_id=bonus_in.user_id,
        amount=bonus_in.amount,
        bonus_type=bonus_in.bonus_type,
        description=bonus_in.description,
        reference_id=bonus_in.reference_id,
        is_paid=True  # Mark as paid immediately
    )
    db.add(bonus)
    
    # Update user's income wallet
    wallet = db.query(IncomeWallet).filter(IncomeWallet.user_id == bonus_in.user_id).first()
    if not wallet:
        wallet = IncomeWallet(user_id=bonus_in.user_id, balance=0.0)
        db.add(wallet)
        db.commit()
        db.refresh(wallet)
    
    # Add the bonus amount to the wallet balance
    wallet.balance += bonus_in.amount
    
    # Create a transaction record
    transaction = IncomeTransaction(
        wallet_id=wallet.id,
        amount=bonus_in.amount,
        transaction_type="CREDIT",
        description=f"Bonus credited: {bonus_in.description}"
    )
    db.add(transaction)
    
    # Commit all changes
    db.commit()
    db.refresh(bonus)
    db.refresh(wallet)
    db.refresh(transaction)
    
    # Send notification to user about bonus credited
    send_bonus_credited_notification(
        db=db,
        user_id=bonus_in.user_id,
        amount=bonus_in.amount,
        bonus_type=bonus_in.bonus_type
    )
    
    return {
        "success": True,
        "bonus": {
            "id": bonus.id,
            "amount": bonus.amount,
            "bonus_type": bonus.bonus_type,
            "description": bonus.description,
            "created_at": bonus.created_at,
            "is_paid": bonus.is_paid
        },
        "wallet_balance": wallet.balance
    }
