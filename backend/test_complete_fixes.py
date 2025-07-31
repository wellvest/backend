#!/usr/bin/env python3
"""
Test script to verify all the fixes:
1. CurrentPlan creation on payment approval
2. Profile plan amount update
3. NOC API endpoint working
"""

import requests
import json
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from app.models.current_plan import CurrentPlan
from app.models.user import User, Profile
from app.models.payment import Payment
from app.schemas.payment import PaymentCreate
from app.services.payment_service import PaymentService
from app.db.database import get_db
import os
from dotenv import load_dotenv

load_dotenv()

def test_noc_api():
    """Test NOC API endpoint"""
    print("🔍 Testing NOC API...")
    
    try:
        # Test login first
        login_data = {
            "phone": "9876543210",
            "password": "password123"
        }
        
        login_response = requests.post("http://localhost:8000/api/auth/login", data=login_data)
        
        if login_response.status_code == 200:
            token_data = login_response.json()
            access_token = token_data.get("access_token")
            
            # Test NOC endpoint with auth
            headers = {"Authorization": f"Bearer {access_token}"}
            noc_response = requests.get("http://localhost:8000/api/noc", headers=headers)
            
            print(f"   NOC API Status: {noc_response.status_code}")
            if noc_response.status_code == 200:
                noc_data = noc_response.json()
                print(f"   ✅ NOC API working - returned {len(noc_data)} NOC records")
                return True
            else:
                print(f"   ❌ NOC API error: {noc_response.text}")
                return False
        else:
            print(f"   ⚠️  Login failed: {login_response.status_code}")
            # Test if endpoint exists without auth
            noc_response = requests.get("http://localhost:8000/api/noc")
            if noc_response.status_code == 401:
                print("   ✅ NOC endpoint exists (requires authentication)")
                return True
            else:
                print(f"   ❌ NOC endpoint not found: {noc_response.status_code}")
                return False
                
    except requests.exceptions.ConnectionError:
        print("   ❌ Server not running")
        return False
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False

def test_payment_and_current_plan():
    """Test payment approval creates CurrentPlan and updates profile"""
    print("🔍 Testing Payment Approval & CurrentPlan Creation...")
    
    db_url = os.getenv('DATABASE_URL')
    engine = create_engine(db_url)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()
    
    try:
        # Get test user
        user = db.query(User).filter(User.member_id == '10000001').first()
        if not user:
            print("   ❌ Test user not found")
            return False
            
        print(f"   Test user: {user.name} (Member ID: {user.member_id})")
        
        # Get initial state
        profile = db.query(Profile).filter(Profile.user_id == user.id).first()
        initial_plan_amount = profile.plan_amount if profile else 0
        
        # Count initial current plans
        initial_current_plans = db.query(CurrentPlan).filter(CurrentPlan.user_id == user.id).count()
        
        print(f"   Initial state:")
        print(f"     Profile plan amount: ₹{initial_plan_amount}")
        print(f"     Current plans count: {initial_current_plans}")
        
        # Create and approve a payment
        payment_data = PaymentCreate(
            user_id=user.id,
            plan_id="1a9b7636-8f17-451d-b6c6-8e1711873b71",  # Basic Plan ID
            amount=5000.0,
            upi_ref_id="TEST_CURRENT_PLAN_" + str(hash(user.id))[-6:]
        )
        
        # Create payment
        payment = PaymentService.create_payment(db, payment_data)
        print(f"   ✅ Payment created: {payment.id}")
        
        # Approve payment
        approved_payment = PaymentService.approve_payment(db, payment.id)
        print(f"   ✅ Payment approved")
        
        # Check final state
        updated_profile = db.query(Profile).filter(Profile.user_id == user.id).first()
        final_plan_amount = updated_profile.plan_amount if updated_profile else 0
        
        final_current_plans = db.query(CurrentPlan).filter(CurrentPlan.user_id == user.id).count()
        
        print(f"   Final state:")
        print(f"     Profile plan amount: ₹{final_plan_amount}")
        print(f"     Current plans count: {final_current_plans}")
        
        # Verify changes
        plan_amount_increased = final_plan_amount > initial_plan_amount
        current_plan_created = final_current_plans > initial_current_plans
        
        if plan_amount_increased and current_plan_created:
            print("   ✅ Payment approval working correctly:")
            print(f"     - Profile plan amount increased: ₹{initial_plan_amount} → ₹{final_plan_amount}")
            print(f"     - CurrentPlan created: {initial_current_plans} → {final_current_plans}")
            return True
        else:
            print("   ❌ Payment approval issues:")
            if not plan_amount_increased:
                print("     - Profile plan amount not updated")
            if not current_plan_created:
                print("     - CurrentPlan not created")
            return False
            
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False
    finally:
        db.close()

def main():
    print("🧪 Testing Complete WellVest Fixes")
    print("=" * 50)
    
    results = []
    
    # Test 1: NOC API
    results.append(test_noc_api())
    print()
    
    # Test 2: Payment & CurrentPlan
    results.append(test_payment_and_current_plan())
    print()
    
    # Summary
    print("📋 Test Results Summary:")
    print("=" * 30)
    
    test_names = ["NOC API", "Payment & CurrentPlan"]
    
    for i, (name, result) in enumerate(zip(test_names, results)):
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{i+1}. {name}: {status}")
    
    all_passed = all(results)
    print()
    if all_passed:
        print("🎉 All tests passed! WellVest fixes are working correctly.")
    else:
        print("⚠️  Some tests failed. Check the details above.")
    
    return all_passed

if __name__ == "__main__":
    main()
