#!/usr/bin/env python3
"""
Test script to verify the complete payment flow works correctly.

This script will:
1. Create a test payment
2. Approve the payment
3. Verify that all data is updated correctly
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy.orm import Session
from app.db.database import SessionLocal
from app.models.user import User, Profile
from app.models.payment import Payment, PaymentStatus
from app.models.plan import Plan
from app.models.wallet import IncomeWallet, IncomeTransaction, TransactionStatus, TransactionType
from app.services.wallet_service import WalletService
from app.services.payment_service import PaymentService
from app.schemas.payment import PaymentCreate
from datetime import datetime
import uuid

def get_db():
    db = SessionLocal()
    try:
        return db
    finally:
        pass

def test_payment_flow():
    """Test the complete payment flow."""
    db = get_db()
    try:
        print("🧪 Testing Payment Flow")
        print("=" * 50)
        
        # Get a test user (first user in the database)
        test_user = db.query(User).first()
        if not test_user:
            print("❌ No users found in database")
            return
        
        print(f"📋 Test User: {test_user.name} ({test_user.member_id})")
        
        # Get a test plan
        test_plan = db.query(Plan).first()
        if not test_plan:
            print("❌ No plans found in database")
            return
        
        print(f"📋 Test Plan: {test_plan.name} - ₹{test_plan.amount}")
        
        # Get initial state
        initial_profile = test_user.profile
        initial_plan_amount = initial_profile.plan_amount if initial_profile else 0
        
        initial_wallet = WalletService.get_or_create_income_wallet(db, test_user.id)
        initial_balance = initial_wallet.balance
        
        print(f"📋 Initial State:")
        print(f"   Profile Plan Amount: ₹{initial_plan_amount}")
        print(f"   Wallet Balance: ₹{initial_balance}")
        
        # Create a test payment
        print(f"\n🔄 Creating test payment...")
        
        # Generate UPI reference for testing
        test_upi_ref = f"TEST{uuid.uuid4().hex[:8].upper()}"
        
        payment_data = PaymentCreate(
            user_id=test_user.id,
            plan_id=test_plan.id,
            amount=test_plan.amount,
            upi_ref_id=test_upi_ref
        )
        
        test_payment = PaymentService.create_payment(
            db=db,
            payment_data=payment_data
        )
        
        print(f"✅ Payment created: {test_payment.id}")
        print(f"   Amount: ₹{test_payment.amount}")
        print(f"   Status: {test_payment.status}")
        
        print(f"🔄 UPI reference: {test_payment.upi_ref_id}")
        
        # Approve the payment
        print(f"\\n🔄 Approving payment...")
        approved_payment = PaymentService.approve_payment(
            db=db,
            payment_id=test_payment.id
        )
        
        print(f"✅ Payment approved!")
        
        # Check final state
        db.refresh(test_user)
        final_profile = test_user.profile
        final_plan_amount = final_profile.plan_amount if final_profile else 0
        
        final_wallet = WalletService.get_or_create_income_wallet(db, test_user.id)
        final_balance = final_wallet.balance
        
        print(f"\\n📋 Final State:")
        print(f"   Profile Plan Amount: ₹{final_plan_amount}")
        print(f"   Wallet Balance: ₹{final_balance}")
        print(f"   Current Plan ID: {final_profile.current_plan_id if final_profile else 'None'}")
        
        # Verify changes
        print(f"\\n🔍 Verification:")
        expected_plan_amount = initial_plan_amount + test_plan.amount
        expected_balance = initial_balance + test_plan.amount
        
        if final_plan_amount == expected_plan_amount:
            print(f"   ✅ Profile plan amount updated correctly: ₹{initial_plan_amount} → ₹{final_plan_amount}")
        else:
            print(f"   ❌ Profile plan amount incorrect: Expected ₹{expected_plan_amount}, got ₹{final_plan_amount}")
        
        if final_balance == expected_balance:
            print(f"   ✅ Wallet balance updated correctly: ₹{initial_balance} → ₹{final_balance}")
        else:
            print(f"   ❌ Wallet balance incorrect: Expected ₹{expected_balance}, got ₹{final_balance}")
        
        if final_profile and final_profile.current_plan_id == test_plan.id:
            print(f"   ✅ Current plan ID updated correctly: {test_plan.id}")
        else:
            print(f"   ❌ Current plan ID not updated correctly")
        
        # Check wallet transactions
        wallet_transactions = db.query(IncomeTransaction).filter(
            IncomeTransaction.wallet_id == final_wallet.id,
            IncomeTransaction.reference_id == test_payment.id
        ).all()
        
        print(f"\\n📋 Wallet Transactions:")
        for txn in wallet_transactions:
            print(f"   - {txn.transaction_type}: ₹{txn.amount} ({txn.status})")
            print(f"     Description: {txn.description}")
        
        if wallet_transactions:
            print(f"   ✅ Wallet transactions created correctly")
        else:
            print(f"   ❌ No wallet transactions found")
        
        print(f"\\n🎉 Payment flow test completed!")
        
    except Exception as e:
        print(f"❌ Error during payment flow test: {e}")
        import traceback
        traceback.print_exc()
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    test_payment_flow()
