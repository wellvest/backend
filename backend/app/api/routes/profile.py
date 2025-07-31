from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.core.auth import get_current_active_user
from app.db.database import get_db
from app.models.user import User, Profile, Address, BankDetail
from app.schemas.user import (
    ProfileCreate, ProfileUpdate, ProfileResponse,
    AddressCreate, AddressUpdate, AddressResponse,
    BankDetailCreate, BankDetailUpdate, BankDetailResponse
)

router = APIRouter()

# Profile routes
@router.post("/profile", response_model=ProfileResponse, status_code=status.HTTP_201_CREATED)
async def create_profile(
    profile_in: ProfileCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Create user profile."""
    # Check if profile already exists
    if current_user.profile:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Profile already exists"
        )
    
    # Create profile
    db_profile = Profile(**profile_in.dict(), user_id=current_user.id)
    db.add(db_profile)
    db.commit()
    db.refresh(db_profile)
    
    return db_profile

@router.get("/profile", response_model=ProfileResponse)
async def get_profile(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get user profile."""
    if not current_user.profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Profile not found"
        )
    
    return current_user.profile

@router.put("/profile", response_model=ProfileResponse)
async def update_profile(
    profile_in: ProfileUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Update user profile."""
    # Create profile if it doesn't exist
    if not current_user.profile:
        db_profile = Profile(user_id=current_user.id)
        db.add(db_profile)
        db.commit()
        db.refresh(current_user)
    
    # Update profile attributes
    for key, value in profile_in.dict(exclude_unset=True).items():
        if value is not None:
            setattr(current_user.profile, key, value)
    
    db.add(current_user.profile)
    db.commit()
    db.refresh(current_user.profile)
    
    return current_user.profile

# Address routes
@router.post("/addresses", response_model=AddressResponse, status_code=status.HTTP_201_CREATED)
async def create_address(
    address_in: AddressCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Create user address."""
    # If this is set as default, unset any existing default
    if address_in.is_default:
        for address in current_user.addresses:
            if address.is_default:
                address.is_default = False
                db.add(address)
    
    # Create address with user data
    address_data = address_in.dict()
    
    # If notes field is empty, pre-populate with user's email
    if not address_data.get('notes'):
        address_data['notes'] = f"Contact: {current_user.email}"
    
    db_address = Address(**address_data, user_id=current_user.id)
    db.add(db_address)
    db.commit()
    db.refresh(db_address)
    
    return db_address

@router.get("/addresses", response_model=List[AddressResponse])
async def get_addresses(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get all user addresses."""
    return current_user.addresses

@router.get("/addresses/{address_id}", response_model=AddressResponse)
async def get_address(
    address_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get specific user address."""
    address = db.query(Address).filter(
        Address.id == address_id,
        Address.user_id == current_user.id
    ).first()
    
    if not address:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Address not found"
        )
    
    return address

@router.put("/addresses/{address_id}", response_model=AddressResponse)
async def update_address(
    address_id: str,
    address_in: AddressUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Update user address."""
    address = db.query(Address).filter(
        Address.id == address_id,
        Address.user_id == current_user.id
    ).first()
    
    if not address:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Address not found"
        )
    
    # If setting as default, unset any existing default
    if address_in.is_default:
        for addr in current_user.addresses:
            if addr.is_default and addr.id != address_id:
                addr.is_default = False
                db.add(addr)
    
    # Update address attributes
    for key, value in address_in.dict(exclude_unset=True).items():
        if value is not None:
            setattr(address, key, value)
    
    db.add(address)
    db.commit()
    db.refresh(address)
    
    return address

@router.delete("/addresses/{address_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_address(
    address_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Delete user address."""
    address = db.query(Address).filter(
        Address.id == address_id,
        Address.user_id == current_user.id
    ).first()
    
    if not address:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Address not found"
        )
    
    db.delete(address)
    db.commit()
    
    return None

# Bank Details routes
@router.post("/bank-details", response_model=BankDetailResponse, status_code=status.HTTP_201_CREATED)
async def create_bank_detail(
    bank_detail_in: BankDetailCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Create user bank detail."""
    # If this is set as default, unset any existing default
    if bank_detail_in.is_default:
        for bank_detail in current_user.bank_details:
            if bank_detail.is_default:
                bank_detail.is_default = False
                db.add(bank_detail)
    
    # Create bank detail
    db_bank_detail = BankDetail(**bank_detail_in.dict(), user_id=current_user.id)
    db.add(db_bank_detail)
    db.commit()
    db.refresh(db_bank_detail)
    
    return db_bank_detail

@router.get("/bank-details", response_model=List[BankDetailResponse])
async def get_bank_details(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get all user bank details."""
    return current_user.bank_details

@router.get("/bank-details/{bank_detail_id}", response_model=BankDetailResponse)
async def get_bank_detail(
    bank_detail_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get specific user bank detail."""
    bank_detail = db.query(BankDetail).filter(
        BankDetail.id == bank_detail_id,
        BankDetail.user_id == current_user.id
    ).first()
    
    if not bank_detail:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Bank detail not found"
        )
    
    return bank_detail

@router.put("/bank-details/{bank_detail_id}", response_model=BankDetailResponse)
async def update_bank_detail(
    bank_detail_id: str,
    bank_detail_in: BankDetailUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Update user bank detail."""
    bank_detail = db.query(BankDetail).filter(
        BankDetail.id == bank_detail_id,
        BankDetail.user_id == current_user.id
    ).first()
    
    if not bank_detail:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Bank detail not found"
        )
    
    # If setting as default, unset any existing default
    if bank_detail_in.is_default:
        for bd in current_user.bank_details:
            if bd.is_default and bd.id != bank_detail_id:
                bd.is_default = False
                db.add(bd)
    
    # Update bank detail attributes
    for key, value in bank_detail_in.dict(exclude_unset=True).items():
        if value is not None:
            setattr(bank_detail, key, value)
    
    db.add(bank_detail)
    db.commit()
    db.refresh(bank_detail)
    
    return bank_detail

@router.delete("/bank-details/{bank_detail_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_bank_detail(
    bank_detail_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Delete user bank detail."""
    bank_detail = db.query(BankDetail).filter(
        BankDetail.id == bank_detail_id,
        BankDetail.user_id == current_user.id
    ).first()
    
    if not bank_detail:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Bank detail not found"
        )
    
    db.delete(bank_detail)
    db.commit()
    
    return None
