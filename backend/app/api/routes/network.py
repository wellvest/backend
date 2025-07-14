from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
import uuid

from app.core.auth import get_current_active_user
from app.db.database import get_db
from app.models.user import User
from app.models.network import Network, Bonus, NOC
from app.schemas.network import (
    NetworkCreate, NetworkUpdate, NetworkResponse, NetworkWithMembersResponse,
    BonusCreate, BonusUpdate, BonusResponse,
    NOCCreate, NOCUpdate, NOCResponse
)

router = APIRouter()

# Network Routes
@router.get("/network", response_model=NetworkWithMembersResponse)
async def get_network(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get the network for the current user with members."""
    # Check if network exists, create if not
    network = db.query(Network).filter(Network.user_id == current_user.id).first()
    if not network:
        # Generate a unique referral code
        referral_code = f"REF-{current_user.member_id}-{uuid.uuid4().hex[:6].upper()}"
        network = Network(user_id=current_user.id, referral_code=referral_code)
        db.add(network)
        db.commit()
        db.refresh(network)
    
    return network

@router.put("/network", response_model=NetworkResponse)
async def update_network(
    network_in: NetworkUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Update the network for the current user."""
    network = db.query(Network).filter(Network.user_id == current_user.id).first()
    if not network:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Network not found"
        )
    
    # Check if referral code is being updated and if it's already taken
    if network_in.referral_code and network_in.referral_code != network.referral_code:
        existing_network = db.query(Network).filter(Network.referral_code == network_in.referral_code).first()
        if existing_network:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Referral code already in use"
            )
    
    # Update network attributes
    for key, value in network_in.dict(exclude_unset=True).items():
        if value is not None:
            setattr(network, key, value)
    
    db.add(network)
    db.commit()
    db.refresh(network)
    
    return network

@router.post("/network/join/{referral_code}", response_model=NetworkResponse)
async def join_network(
    referral_code: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Join a network using a referral code."""
    # Find the network with the given referral code
    network = db.query(Network).filter(Network.referral_code == referral_code).first()
    if not network:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Network not found with the given referral code"
        )
    
    # Check if user is already in a network
    user_network = db.query(Network).filter(Network.user_id == current_user.id).first()
    if user_network and user_network.referred_by:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User is already in a network"
        )
    
    # Create or update user's network
    if not user_network:
        # Generate a unique referral code
        new_referral_code = f"REF-{current_user.member_id}-{uuid.uuid4().hex[:6].upper()}"
        user_network = Network(
            user_id=current_user.id,
            referral_code=new_referral_code,
            referred_by=network.user_id
        )
        db.add(user_network)
    else:
        user_network.referred_by = network.user_id
        db.add(user_network)
    
    # Add user to the referrer's network members
    if current_user.id not in [member.id for member in network.members]:
        network.members.append(current_user)
        network.total_members += 1
        db.add(network)
    
    db.commit()
    db.refresh(user_network)
    
    return user_network

# Bonus Routes
@router.get("/bonuses", response_model=List[BonusResponse])
async def get_bonuses(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get all bonuses for the current user."""
    return current_user.bonuses

@router.post("/bonuses", response_model=BonusResponse, status_code=status.HTTP_201_CREATED)
async def create_bonus(
    bonus_in: BonusCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Create a new bonus for the current user."""
    db_bonus = Bonus(**bonus_in.dict(), user_id=current_user.id)
    db.add(db_bonus)
    db.commit()
    db.refresh(db_bonus)
    
    return db_bonus

@router.put("/bonuses/{bonus_id}", response_model=BonusResponse)
async def update_bonus(
    bonus_id: str,
    bonus_in: BonusUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Update a bonus."""
    bonus = db.query(Bonus).filter(
        Bonus.id == bonus_id,
        Bonus.user_id == current_user.id
    ).first()
    
    if not bonus:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Bonus not found"
        )
    
    # Update bonus attributes
    for key, value in bonus_in.dict(exclude_unset=True).items():
        if value is not None:
            setattr(bonus, key, value)
    
    db.add(bonus)
    db.commit()
    db.refresh(bonus)
    
    return bonus

# NOC Routes
@router.get("/noc", response_model=List[NOCResponse])
async def get_nocs(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get all NOCs for the current user."""
    nocs = db.query(NOC).filter(NOC.user_id == current_user.id).all()
    return nocs

@router.post("/noc", response_model=NOCResponse, status_code=status.HTTP_201_CREATED)
async def create_noc(
    noc_in: NOCCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Create a new NOC for the current user."""
    db_noc = NOC(**noc_in.dict(), user_id=current_user.id)
    db.add(db_noc)
    db.commit()
    db.refresh(db_noc)
    
    return db_noc

@router.put("/noc/{noc_id}", response_model=NOCResponse)
async def update_noc(
    noc_id: str,
    noc_in: NOCUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Update a NOC."""
    noc = db.query(NOC).filter(
        NOC.id == noc_id,
        NOC.user_id == current_user.id
    ).first()
    
    if not noc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="NOC not found"
        )
    
    # Update NOC attributes
    for key, value in noc_in.dict(exclude_unset=True).items():
        if value is not None:
            setattr(noc, key, value)
    
    db.add(noc)
    db.commit()
    db.refresh(noc)
    
    return noc
