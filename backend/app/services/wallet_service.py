from sqlalchemy.orm import Session
from typing import Optional, List
from datetime import datetime

from app.models.wallet import (
    IncomeWallet, ShoppingWallet, 
    IncomeTransaction, ShoppingTransaction,
    TransactionType, TransactionStatus
)

class WalletService:
    @staticmethod
    def get_or_create_income_wallet(db: Session, user_id: str) -> IncomeWallet:
        """
        Get or create an income wallet for a user.
        """
        wallet = db.query(IncomeWallet).filter(IncomeWallet.user_id == user_id).first()
        if not wallet:
            wallet = IncomeWallet(user_id=user_id, balance=0.0)
            db.add(wallet)
            db.commit()
            db.refresh(wallet)
        return wallet
    
    @staticmethod
    def get_or_create_shopping_wallet(db: Session, user_id: str) -> ShoppingWallet:
        """
        Get or create a shopping wallet for a user.
        """
        wallet = db.query(ShoppingWallet).filter(ShoppingWallet.user_id == user_id).first()
        if not wallet:
            wallet = ShoppingWallet(user_id=user_id, balance=0.0)
            db.add(wallet)
            db.commit()
            db.refresh(wallet)
        return wallet
    
    @staticmethod
    def add_income_transaction(
        db: Session, 
        user_id: str, 
        amount: float, 
        transaction_type: TransactionType,
        status: TransactionStatus = TransactionStatus.PENDING,
        description: Optional[str] = None,
        reference_id: Optional[str] = None
    ) -> IncomeTransaction:
        """
        Add a transaction to a user's income wallet.
        """
        # Get or create wallet
        wallet = WalletService.get_or_create_income_wallet(db, user_id)
        
        # Create transaction
        transaction = IncomeTransaction(
            wallet_id=wallet.id,
            amount=amount,
            transaction_type=transaction_type,
            status=status,
            description=description,
            reference_id=reference_id
        )
        db.add(transaction)
        
        # Update wallet balance if transaction is completed
        if status == TransactionStatus.COMPLETED:
            if transaction_type == TransactionType.CREDIT:
                wallet.balance += amount
            elif transaction_type == TransactionType.DEBIT:
                wallet.balance = max(0, wallet.balance - amount)
            db.add(wallet)
        
        db.commit()
        db.refresh(transaction)
        return transaction
    
    @staticmethod
    def update_transaction_status(
        db: Session,
        transaction_id: str,
        new_status: TransactionStatus
    ) -> Optional[IncomeTransaction]:
        """
        Update the status of an income transaction and update wallet balance if needed.
        """
        transaction = db.query(IncomeTransaction).filter(IncomeTransaction.id == transaction_id).first()
        if not transaction:
            return None
        
        old_status = transaction.status
        transaction.status = new_status
        
        # Update wallet balance if transaction is being completed
        if old_status != TransactionStatus.COMPLETED and new_status == TransactionStatus.COMPLETED:
            wallet = transaction.wallet
            if transaction.transaction_type == TransactionType.CREDIT:
                wallet.balance += transaction.amount
            elif transaction.transaction_type == TransactionType.DEBIT:
                wallet.balance = max(0, wallet.balance - transaction.amount)
            db.add(wallet)
        # No wallet balance update needed for REJECTED or FAILED status
        # as the transaction was never completed
        
        db.add(transaction)
        db.commit()
        db.refresh(transaction)
        return transaction
    
    @staticmethod
    def get_income_transactions(
        db: Session,
        user_id: str,
        skip: int = 0,
        limit: int = 100
    ) -> List[IncomeTransaction]:
        """
        Get income transactions for a user.
        """
        wallet = WalletService.get_or_create_income_wallet(db, user_id)
        return db.query(IncomeTransaction).filter(
            IncomeTransaction.wallet_id == wallet.id
        ).order_by(IncomeTransaction.created_at.desc()).offset(skip).limit(limit).all()
    
    @staticmethod
    def get_pending_income_transactions(
        db: Session,
        user_id: str,
        skip: int = 0,
        limit: int = 100
    ) -> List[IncomeTransaction]:
        """
        Get pending income transactions for a user.
        """
        wallet = WalletService.get_or_create_income_wallet(db, user_id)
        return db.query(IncomeTransaction).filter(
            IncomeTransaction.wallet_id == wallet.id,
            IncomeTransaction.status == TransactionStatus.PENDING
        ).order_by(IncomeTransaction.created_at.desc()).offset(skip).limit(limit).all()
