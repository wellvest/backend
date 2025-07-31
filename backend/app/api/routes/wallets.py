from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.core.auth import get_current_active_user
from app.db.database import get_db
from app.models.user import User
from app.models.wallet import (
    IncomeWallet, IncomeTransaction, 
    ShoppingWallet, ShoppingTransaction, ShoppingVoucher
)
from app.schemas.wallet import (
    IncomeWalletCreate, IncomeWalletUpdate, IncomeWalletResponse,
    IncomeTransactionCreate, IncomeTransactionUpdate, IncomeTransactionResponse,
    ShoppingWalletCreate, ShoppingWalletUpdate, ShoppingWalletResponse,
    ShoppingTransactionCreate, ShoppingTransactionUpdate, ShoppingTransactionResponse,
    ShoppingVoucherCreate, ShoppingVoucherUpdate, ShoppingVoucherResponse,
    IncomeWalletWithTransactionsResponse, ShoppingWalletWithTransactionsResponse
)

router = APIRouter()

# Income Wallet Routes
@router.get("/income-wallet", response_model=IncomeWalletWithTransactionsResponse)
async def get_income_wallet(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get the income wallet for the current user with transactions."""
    from app.services.wallet_service import WalletService
    
    # Get or create wallet
    wallet = WalletService.get_or_create_income_wallet(db, current_user.id)
    
    # Recalculate balance to ensure it's accurate
    WalletService.recalculate_income_wallet_balance(db, current_user.id)
    
    # Refresh wallet to get updated balance
    db.refresh(wallet)
    
    return wallet

@router.post("/income-wallet/transactions", response_model=IncomeTransactionResponse, status_code=status.HTTP_201_CREATED)
async def create_income_transaction(
    transaction_in: IncomeTransactionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Create a new income wallet transaction."""
    # Get or create wallet
    wallet = db.query(IncomeWallet).filter(IncomeWallet.user_id == current_user.id).first()
    if not wallet:
        wallet = IncomeWallet(user_id=current_user.id)
        db.add(wallet)
        db.commit()
        db.refresh(wallet)
    
    # Create transaction
    db_transaction = IncomeTransaction(**transaction_in.dict(), wallet_id=wallet.id)
    db.add(db_transaction)
    
    # Update wallet balance
    if transaction_in.transaction_type == "credit":
        wallet.balance += transaction_in.amount
    elif transaction_in.transaction_type == "debit":
        if wallet.balance < transaction_in.amount:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Insufficient balance"
            )
        wallet.balance -= transaction_in.amount
    
    db.add(wallet)
    db.commit()
    db.refresh(db_transaction)
    
    return db_transaction

@router.get("/income-wallet/transactions", response_model=List[IncomeTransactionResponse])
async def get_income_transactions(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get all income wallet transactions for the current user."""
    wallet = db.query(IncomeWallet).filter(IncomeWallet.user_id == current_user.id).first()
    if not wallet:
        return []
    
    return wallet.transactions

@router.put("/income-wallet/transactions/{transaction_id}", response_model=IncomeTransactionResponse)
async def update_income_transaction(
    transaction_id: str,
    transaction_in: IncomeTransactionUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Update an income wallet transaction."""
    wallet = db.query(IncomeWallet).filter(IncomeWallet.user_id == current_user.id).first()
    if not wallet:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Wallet not found"
        )
    
    transaction = db.query(IncomeTransaction).filter(
        IncomeTransaction.id == transaction_id,
        IncomeTransaction.wallet_id == wallet.id
    ).first()
    
    if not transaction:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Transaction not found"
        )
    
    # Update transaction attributes
    for key, value in transaction_in.dict(exclude_unset=True).items():
        if value is not None:
            setattr(transaction, key, value)
    
    db.add(transaction)
    db.commit()
    db.refresh(transaction)
    
    return transaction

# Shopping Wallet Routes
@router.get("/shopping-wallet", response_model=ShoppingWalletWithTransactionsResponse)
async def get_shopping_wallet(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get the shopping wallet for the current user with transactions and vouchers."""
    # Check if wallet exists, create if not
    wallet = db.query(ShoppingWallet).filter(ShoppingWallet.user_id == current_user.id).first()
    if not wallet:
        wallet = ShoppingWallet(user_id=current_user.id)
        db.add(wallet)
        db.commit()
        db.refresh(wallet)
    
    return wallet

@router.post("/shopping-wallet/transactions", response_model=ShoppingTransactionResponse, status_code=status.HTTP_201_CREATED)
async def create_shopping_transaction(
    transaction_in: ShoppingTransactionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Create a new shopping wallet transaction."""
    # Get or create wallet
    wallet = db.query(ShoppingWallet).filter(ShoppingWallet.user_id == current_user.id).first()
    if not wallet:
        wallet = ShoppingWallet(user_id=current_user.id)
        db.add(wallet)
        db.commit()
        db.refresh(wallet)
    
    # Create transaction
    db_transaction = ShoppingTransaction(**transaction_in.dict(), wallet_id=wallet.id)
    db.add(db_transaction)
    
    # Update wallet balance
    if transaction_in.transaction_type == "credit":
        wallet.balance += transaction_in.amount
    elif transaction_in.transaction_type == "debit":
        if wallet.balance < transaction_in.amount:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Insufficient balance"
            )
        wallet.balance -= transaction_in.amount
    
    db.add(wallet)
    db.commit()
    db.refresh(db_transaction)
    
    return db_transaction

@router.get("/shopping-wallet/transactions", response_model=List[ShoppingTransactionResponse])
async def get_shopping_transactions(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get all shopping wallet transactions for the current user."""
    wallet = db.query(ShoppingWallet).filter(ShoppingWallet.user_id == current_user.id).first()
    if not wallet:
        return []
    
    return wallet.transactions

# Shopping Voucher Routes
@router.post("/shopping-wallet/vouchers", response_model=ShoppingVoucherResponse, status_code=status.HTTP_201_CREATED)
async def create_shopping_voucher(
    voucher_in: ShoppingVoucherCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Create a new shopping voucher."""
    # Get or create wallet
    wallet = db.query(ShoppingWallet).filter(ShoppingWallet.user_id == current_user.id).first()
    if not wallet:
        wallet = ShoppingWallet(user_id=current_user.id)
        db.add(wallet)
        db.commit()
        db.refresh(wallet)
    
    # Check if voucher code already exists
    existing_voucher = db.query(ShoppingVoucher).filter(ShoppingVoucher.code == voucher_in.code).first()
    if existing_voucher:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Voucher code already exists"
        )
    
    # Create voucher
    db_voucher = ShoppingVoucher(**voucher_in.dict(), wallet_id=wallet.id)
    db.add(db_voucher)
    db.commit()
    db.refresh(db_voucher)
    
    return db_voucher

@router.get("/shopping-wallet/vouchers", response_model=List[ShoppingVoucherResponse])
async def get_shopping_vouchers(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get all shopping vouchers for the current user."""
    wallet = db.query(ShoppingWallet).filter(ShoppingWallet.user_id == current_user.id).first()
    if not wallet:
        return []
    
    return wallet.vouchers

@router.put("/shopping-wallet/vouchers/{voucher_id}", response_model=ShoppingVoucherResponse)
async def update_shopping_voucher(
    voucher_id: str,
    voucher_in: ShoppingVoucherUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Update a shopping voucher."""
    wallet = db.query(ShoppingWallet).filter(ShoppingWallet.user_id == current_user.id).first()
    if not wallet:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Wallet not found"
        )
    
    voucher = db.query(ShoppingVoucher).filter(
        ShoppingVoucher.id == voucher_id,
        ShoppingVoucher.wallet_id == wallet.id
    ).first()
    
    if not voucher:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Voucher not found"
        )
    
    # Update voucher attributes
    for key, value in voucher_in.dict(exclude_unset=True).items():
        if value is not None:
            setattr(voucher, key, value)
    
    db.add(voucher)
    db.commit()
    db.refresh(voucher)
    
    return voucher
