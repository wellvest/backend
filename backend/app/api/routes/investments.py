from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Dict, Any
from app.services.bonus_service import BonusService

from app.core.auth import get_current_active_user
from app.db.database import get_db
from app.models.user import User
from app.models.investment import Investment, TeamInvestment
from app.models.plan import Plan
from app.schemas.investment import (
    InvestmentCreate, InvestmentUpdate, InvestmentResponse,
    TeamInvestmentCreate, TeamInvestmentResponse,
    InvestmentWithTeamResponse
)
from app.utils.notification_utils import send_plan_selection_notification

router = APIRouter()

@router.post("/investments", response_model=Dict[str, Any], status_code=status.HTTP_201_CREATED)
async def create_investment(
    investment_in: InvestmentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Create a new investment for the current user."""
    # Get plan details if plan_id is provided
    plan_name = "Investment Plan"
    if hasattr(investment_in, 'plan_id') and investment_in.plan_id:
        plan = db.query(Plan).filter(Plan.id == investment_in.plan_id).first()
        if plan:
            plan_name = plan.name
    
    db_investment = Investment(**investment_in.dict(), user_id=current_user.id)
    db.add(db_investment)
    db.commit()
    db.refresh(db_investment)
    
    # Process referral bonuses
    bonus_result = await BonusService.process_referral_bonus(
        db=db,
        user_id=current_user.id,
        plan_amount=investment_in.amount
    )
    
    # Send notification to user about plan selection
    send_plan_selection_notification(
        db=db,
        user_id=current_user.id,
        plan_name=plan_name,
        amount=investment_in.amount
    )
    
    return {
        "investment": db_investment,
        "bonus_distribution": bonus_result
    }

@router.get("/investments", response_model=List[InvestmentResponse])
async def get_investments(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get all investments for the current user."""
    return current_user.investments

@router.get("/investments/{investment_id}", response_model=InvestmentWithTeamResponse)
async def get_investment(
    investment_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get a specific investment with team investments."""
    investment = db.query(Investment).filter(
        Investment.id == investment_id,
        Investment.user_id == current_user.id
    ).first()
    
    if not investment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Investment not found"
        )
    
    return investment

@router.put("/investments/{investment_id}", response_model=InvestmentResponse)
async def update_investment(
    investment_id: str,
    investment_in: InvestmentUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Update a specific investment."""
    investment = db.query(Investment).filter(
        Investment.id == investment_id,
        Investment.user_id == current_user.id
    ).first()
    
    if not investment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Investment not found"
        )
    
    # Update investment attributes
    for key, value in investment_in.dict(exclude_unset=True).items():
        if value is not None:
            setattr(investment, key, value)
    
    db.add(investment)
    db.commit()
    db.refresh(investment)
    
    return investment

@router.get("/team-investments", response_model=List[TeamInvestmentResponse])
async def get_team_investments(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get all team investments where the current user is a team member."""
    team_investments = db.query(TeamInvestment).filter(
        TeamInvestment.team_member_id == current_user.id
    ).all()
    
    return team_investments

@router.post("/team-investments", response_model=TeamInvestmentResponse, status_code=status.HTTP_201_CREATED)
async def create_team_investment(
    team_investment_in: TeamInvestmentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Create a new team investment."""
    # Verify the investment exists and belongs to the current user
    investment = db.query(Investment).filter(
        Investment.id == team_investment_in.investment_id,
        Investment.user_id == current_user.id
    ).first()
    
    if not investment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Investment not found"
        )
    
    # Verify the team member exists
    team_member = db.query(User).filter(User.id == team_investment_in.team_member_id).first()
    if not team_member:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Team member not found"
        )
    
    db_team_investment = TeamInvestment(**team_investment_in.dict())
    db.add(db_team_investment)
    db.commit()
    db.refresh(db_team_investment)
    
    # Send notification to team leader about new team member
    from app.utils.notification_utils import send_team_member_joined_notification
    send_team_member_joined_notification(
        db=db,
        team_leader_id=current_user.id,
        member_name=team_member.name if team_member.name else "A new member"
    )
    
    return db_team_investment
