#!/usr/bin/env python3
"""
Script to fix and verify the payment flow in WellVest application.

This script will:
1. Check and fix wallet balance calculations
2. Verify payment approval process
3. Ensure profile plan_amount is updated correctly
4. Test the complete payment flow
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy.orm import Session
from sqlalchemy import func
from app.db.database import SessionLocal, engine
from app.models.user import User, Profile
from app.models.payment import Payment, PaymentStatus
from app.models.plan import Plan
from app.models.wallet import IncomeWallet, IncomeTransaction, TransactionStatus, TransactionType
from app.services.wallet_service import WalletService
from app.services.payment_service import PaymentService
from datetime import datetime

def get_db():
    db = SessionLocal()
    try:
        return db
    finally:
        pass

def fix_wallet_balances():
    """Fix all wallet balances by recalculating from transactions."""
    db = get_db()
    try:
        print("🔧 Fixing wallet balances...")
        
        # Get all users with wallets
        users_with_wallets = db.query(User).join(IncomeWallet).all()
        
        for user in users_with_wallets:
            old_balance = user.income_wallet.balance if user.income_wallet else 0
            new_balance = WalletService.recalculate_income_wallet_balance(db, user.id)
            
            if old_balance != new_balance:
                print(f"  ✅ Fixed {user.name} ({user.member_id}): {old_balance} → {new_balance}")
            else:
                print(f"  ✓ {user.name} ({user.member_id}): {new_balance} (no change)")
        
        print("✅ Wallet balance fix completed!")
        
    except Exception as e:
        print(f"❌ Error fixing wallet balances: {e}")
        db.rollback()
    finally:
        db.close()

def verify_payment_flow():
    """Verify the payment flow by checking recent payments."""
    db = get_db()
    try:
        print("\n🔍 Verifying payment flow...")
        
        # Get recent payments
        recent_payments = db.query(Payment).order_by(Payment.created_at.desc()).limit(10).all()
        
        for payment in recent_payments:
            print(f"\n📋 Payment ID: {payment.id}")
            print(f"   User: {payment.user.name if payment.user else 'Unknown'} ({payment.user.member_id if payment.user else 'N/A'})")
            print(f"   Amount: ₹{payment.amount}")
            print(f"   Status: {payment.status}")
            print(f"   Plan: {payment.plan.name if payment.plan else 'N/A'}")
            
            # Check user profile
            profile = payment.user.profile
            if profile:
                print(f"   Profile Plan Amount: ₹{profile.plan_amount}")
                print(f"   Current Plan ID: {profile.current_plan_id}")
                
                # Check if plan amount matches approved payments
                if payment.status == PaymentStatus.APPROVED:
                    user_approved_payments = db.query(Payment).filter(
                        Payment.user_id == payment.user_id,
                        Payment.status == PaymentStatus.APPROVED
                    ).all()
                    total_approved = sum(p.amount for p in user_approved_payments)
                    
                    if profile.plan_amount != total_approved:
                        print(f"   ⚠️  Plan amount mismatch! Profile: ₹{profile.plan_amount}, Total approved: ₹{total_approved}")
                    else:
                        print(f"   ✅ Plan amount matches approved payments")
            
            # Check wallet transactions
            if payment.user.income_wallet:
                wallet_transactions = db.query(IncomeTransaction).filter(
                    IncomeTransaction.wallet_id == payment.user.income_wallet.id,
                    IncomeTransaction.reference_id == payment.id
                ).all()
                
                print(f"   Wallet Transactions: {len(wallet_transactions)}")
                for txn in wallet_transactions:
                    print(f"     - {txn.transaction_type}: ₹{txn.amount} ({txn.status})")
        
        print("\n✅ Payment flow verification completed!")
        
    except Exception as e:
        print(f"❌ Error verifying payment flow: {e}")
    finally:
        db.close()

def fix_profile_plan_amounts():
    """Fix profile plan amounts based on approved payments."""
    db = get_db()
    try:
        print("\n🔧 Fixing profile plan amounts...")
        
        # Get all users with profiles
        users = db.query(User).filter(User.profile != None).all()
        
        for user in users:
            # Calculate total approved payments
            approved_payments = db.query(Payment).filter(
                Payment.user_id == user.id,
                Payment.status == PaymentStatus.APPROVED
            ).all()
            
            total_approved = sum(p.amount for p in approved_payments)
            current_plan_amount = user.profile.plan_amount or 0
            
            if total_approved != current_plan_amount:
                print(f"  🔧 Fixing {user.name} ({user.member_id}): ₹{current_plan_amount} → ₹{total_approved}")
                user.profile.plan_amount = total_approved
                
                # Set current plan ID to the latest approved payment's plan
                if approved_payments:
                    latest_payment = max(approved_payments, key=lambda p: p.created_at)
                    user.profile.current_plan_id = latest_payment.plan_id
                
                db.add(user.profile)
            else:
                print(f"  ✓ {user.name} ({user.member_id}): ₹{total_approved} (correct)")
        
        db.commit()
        print("✅ Profile plan amount fix completed!")
        
    except Exception as e:
        print(f"❌ Error fixing profile plan amounts: {e}")
        db.rollback()
    finally:
        db.close()

def show_summary():
    """Show a summary of the current state."""
    db = get_db()
    try:
        print("\n📊 SUMMARY")
        print("=" * 50)
        
        # Count users with plans
        users_with_plans = db.query(User).join(Profile).filter(Profile.plan_amount > 0).count()
        total_users = db.query(User).count()
        
        print(f"Total Users: {total_users}")
        print(f"Users with Plans: {users_with_plans}")
        
        # Payment statistics
        total_payments = db.query(Payment).count()
        pending_payments = db.query(Payment).filter(Payment.status == PaymentStatus.PENDING).count()
        approved_payments = db.query(Payment).filter(Payment.status == PaymentStatus.APPROVED).count()
        rejected_payments = db.query(Payment).filter(Payment.status == PaymentStatus.REJECTED).count()
        
        print(f"\nPayments:")
        print(f"  Total: {total_payments}")
        print(f"  Pending: {pending_payments}")
        print(f"  Approved: {approved_payments}")
        print(f"  Rejected: {rejected_payments}")
        
        # Total investment amount
        total_investment = db.query(func.sum(Payment.amount)).filter(Payment.status == PaymentStatus.APPROVED).scalar() or 0
        
        print(f"\nTotal Investment Amount: ₹{total_investment:,.2f}")
        
        # Wallet statistics
        total_wallet_balance = db.query(func.sum(IncomeWallet.balance)).scalar() or 0
        
        print(f"Total Wallet Balance: ₹{total_wallet_balance:,.2f}")
        
    except Exception as e:
        print(f"❌ Error generating summary: {e}")
    finally:
        db.close()

def main():
    print("🚀 WellVest Payment Flow Fix Script")
    print("=" * 50)
    
    # Step 1: Fix wallet balances
    fix_wallet_balances()
    
    # Step 2: Fix profile plan amounts
    fix_profile_plan_amounts()
    
    # Step 3: Verify payment flow
    verify_payment_flow()
    
    # Step 4: Show summary
    show_summary()
    
    print("\n🎉 All fixes completed!")
    print("\nNext steps:")
    print("1. Test payment creation and approval")
    print("2. Verify that current plan shows correctly in frontend")
    print("3. Check that wallet balance updates properly")
    print("4. Ensure profile plan amount displays correctly")

if __name__ == "__main__":
    main()
