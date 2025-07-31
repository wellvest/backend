from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.core.auth import get_current_active_user
from app.db.database import get_db
from app.models.user import User
from app.schemas.user import UserResponse

router = APIRouter()

@router.get("/referrals/my-code", response_model=dict)
async def get_my_referral_code(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get the current user's referral code and referral link."""
    # Check if user has a referral code, if not generate one
    if not current_user.referral_code and current_user.member_id:
        # Generate a referral code based on member_id
        referral_code = f"WV{current_user.member_id}"
        
        # Update the user with the new referral code
        current_user.referral_code = referral_code
        db.add(current_user)
        db.commit()
        db.refresh(current_user)
    
    # If still no referral code (e.g., no member_id), return empty
    if not current_user.referral_code:
        return {
            "referral_code": "",
            "referral_link": ""
        }
    
    # Use relative URL for development environment
    base_url = "/#/signup?ref="
    referral_link = f"{base_url}{current_user.referral_code}"
    
    return {
        "referral_code": current_user.referral_code,
        "referral_link": referral_link
    }

@router.get("/referrals/my-referrals", response_model=List[UserResponse])
async def get_my_referrals(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get list of users referred by the current user."""
    referrals = db.query(User).filter(User.referrer_id == current_user.id).all()
    return referrals

@router.get("/referrals/network-data")
async def get_network_data(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get network data including summary and team members."""
    # Get direct referrals
    direct_referrals = db.query(User).filter(User.referrer_id == current_user.id).all()
    
    # Get all referrals (including indirect)
    all_referrals = []
    processed_ids = set()
    
    def get_downline(user_id, level=0, max_level=2):
        if level > max_level:
            return []
        
        if user_id in processed_ids:
            return []  # Prevent circular references
        
        processed_ids.add(user_id)
        referrals = db.query(User).filter(User.referrer_id == user_id).all()
        result = []
        
        for referral in referrals:
            all_referrals.append(referral)
            children = get_downline(referral.id, level + 1, max_level)
            result.append({
                "id": referral.id,
                "name": referral.name,
                "userId": referral.member_id or "",
                "level": level,
                "status": "Active",  # Default status, could be dynamic
                "children": children
            })
        
        return result
    
    # Build network tree
    network_tree = {
        "id": current_user.id,
        "name": current_user.name,
        "userId": current_user.member_id or "",
        "level": 0,
        "status": "Active",
        "children": get_downline(current_user.id)
    }
    
    # Count active/inactive members
    active_count = len(all_referrals)  # For now, count all as active
    inactive_count = 0
    blocked_count = 0
    
    # Format team members for display
    team_members = []
    for referral in direct_referrals:
        team_members.append({
            "id": referral.id,
            "name": referral.name,
            "userId": referral.member_id or "",
            "status": "Active",  # Default status, could be dynamic
            "joinDate": referral.join_date.strftime("%Y-%m-%d") if referral.join_date else "",
            "avatar": referral.avatar or ""
        })
    
    return {
        "summary": {
            "downline": current_user.member_id or "",
            "activeCount": active_count,
            "inactiveCount": inactive_count,
            "blockedCount": blocked_count,
            "totalCount": len(all_referrals)
        },
        "teamMembers": team_members,
        "networkTree": network_tree
    }
