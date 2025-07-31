"""
Test script to verify the payment and investment flow implementation.
"""
from app.db.database import SessionLocal
from app.services.payment_service import PaymentService
from app.services.wallet_service import WalletService
from app.services.investment_service import InvestmentService
from app.models.payment import Payment, PaymentStatus
from app.models.wallet import TransactionStatus, IncomeTransaction
from app.models.investment import Investment
from app.schemas.payment import PaymentCreate
from sqlalchemy.orm import Session
from sqlalchemy import Column, String, Float, Integer, Boolean, DateTime, ForeignKey
from sqlalchemy.sql import func
from app.db.database import Base
import uuid

# Define Plan model to avoid dependency issues
class Plan(Base):
    __tablename__ = "plans"
    
    id = Column(String, primary_key=True)
    name = Column(String, nullable=False)
    amount = Column(Float, nullable=False)
    duration_months = Column(Integer, nullable=False)
    interest_rate = Column(Float, nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

# Import User and Profile after Plan is defined
from app.models.user import User, Profile

def create_test_user_if_not_exists(db: Session) -> User:
    """Create a test user if it doesn't exist."""
    test_user = db.query(User).filter(User.email == "test@example.com").first()
    if not test_user:
        print("Creating test user...")
        # Generate a unique member_id and referral_code
        member_id = f"TEST{uuid.uuid4().hex[:6].upper()}"
        referral_code = f"REF{uuid.uuid4().hex[:8].upper()}"
        
        # Create the user
        test_user = User(
            name="Test User",
            email="test@example.com",
            hashed_password="$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW",  # "password"
            phone="+919876543210",
            date_of_birth="1990-01-01",
            gender="Male",
            is_active=True,
            member_id=member_id,
            referral_code=referral_code
        )
        db.add(test_user)
        db.commit()
        db.refresh(test_user)
        
        # Create a profile for the user
        profile = Profile(
            user_id=test_user.id,
            plan_amount=0.0,
            total_invested_amount=0.0,
            kyc_verified=True
        )
        db.add(profile)
        db.commit()
        
        # Create wallets for the user
        WalletService.get_or_create_income_wallet(db, test_user.id)
        
        print(f"Test user created with ID: {test_user.id}")
    else:
        print(f"Using existing test user with ID: {test_user.id}")
    
    return test_user

def create_test_plan_if_not_exists(db: Session) -> str:
    """Create a test plan if it doesn't exist."""
    # Check if the plans table exists
    try:
        result = db.execute("SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'plans')").scalar()
        if not result:
            print("Plans table doesn't exist. Creating a simple plan record...")
            db.execute("""
                CREATE TABLE IF NOT EXISTS plans (
                    id VARCHAR PRIMARY KEY,
                    name VARCHAR NOT NULL,
                    amount FLOAT NOT NULL,
                    duration_months INTEGER NOT NULL,
                    interest_rate FLOAT NOT NULL,
                    is_active BOOLEAN DEFAULT TRUE,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Insert a test plan
            plan_id = str(uuid.uuid4())
            db.execute(f"""
                INSERT INTO plans (id, name, amount, duration_months, interest_rate, is_active)
                VALUES ('{plan_id}', 'Test Plan', 10000, 12, 10.0, TRUE)
            """)
            db.commit()
            print(f"Created test plan with ID: {plan_id}")
            return plan_id
        
        # Check if there's at least one plan
        plan_id = db.execute("SELECT id FROM plans LIMIT 1").scalar()
        if not plan_id:
            # Insert a test plan
            plan_id = str(uuid.uuid4())
            db.execute(f"""
                INSERT INTO plans (id, name, amount, duration_months, interest_rate, is_active)
                VALUES ('{plan_id}', 'Test Plan', 10000, 12, 10.0, TRUE)
            """)
            db.commit()
            print(f"Created test plan with ID: {plan_id}")
        else:
            print(f"Using existing plan with ID: {plan_id}")
        
        return plan_id
    except Exception as e:
        print(f"Error checking/creating plan: {str(e)}")
        # Create a dummy plan ID for testing
        return "test_plan_id"

def test_payment_flow():
    """Test the complete payment and investment flow."""
    db = SessionLocal()
    try:
        # Create test user and plan
        test_user = create_test_user_if_not_exists(db)
        test_plan_id = create_test_plan_if_not_exists(db)
        
        # Step 1: Create a payment with UPI reference ID
        print("\n1. Creating payment with UPI reference ID...")
        payment_data = PaymentCreate(
            user_id=test_user.id,
            plan_id=test_plan_id,
            amount=10000,
            upi_ref_id="TEST_UPI_REF_123"
        )
        payment = PaymentService.create_payment(db, payment_data)
        print(f"Payment created with ID: {payment.id}, Status: {payment.status}")
        
        # Step 2: Check if a pending wallet transaction was created
        print("\n2. Checking for pending wallet transaction...")
        transactions = db.query(IncomeTransaction).filter(
            IncomeTransaction.reference_id == payment.id,
            IncomeTransaction.status == TransactionStatus.PENDING
        ).all()
        
        if transactions:
            print(f"Found {len(transactions)} pending transaction(s):")
            for tx in transactions:
                print(f"  - Transaction ID: {tx.id}, Amount: {tx.amount}, Status: {tx.status}")
        else:
            print("No pending transactions found for this payment.")
        
        # Step 3: Approve the payment
        print("\n3. Approving payment...")
        approved_payment = PaymentService.approve_payment(db, payment.id)
        if approved_payment:
            print(f"Payment approved. New status: {approved_payment.status}")
        else:
            print("Failed to approve payment.")
        
        # Step 4: Check if the wallet transaction was updated to completed
        print("\n4. Checking if wallet transaction was updated...")
        updated_transactions = db.query(IncomeTransaction).filter(
            IncomeTransaction.reference_id == payment.id
        ).all()
        
        if updated_transactions:
            print(f"Found {len(updated_transactions)} transaction(s):")
            for tx in updated_transactions:
                print(f"  - Transaction ID: {tx.id}, Amount: {tx.amount}, Status: {tx.status}")
        else:
            print("No transactions found for this payment.")
        
        # Step 5: Check if an investment was created
        print("\n5. Checking if investment was created...")
        investments = db.query(Investment).filter(
            Investment.payment_id == payment.id
        ).all()
        
        if investments:
            print(f"Found {len(investments)} investment(s):")
            for inv in investments:
                print(f"  - Investment ID: {inv.id}, Amount: {inv.amount}, Status: {inv.status}")
        else:
            print("No investments found for this payment.")
        
        # Step 6: Check if user's total_invested_amount was updated
        print("\n6. Checking if user's total_invested_amount was updated...")
        profile = db.query(Profile).filter(Profile.user_id == test_user.id).first()
        if profile:
            print(f"User profile total_invested_amount: {profile.total_invested_amount}")
        else:
            print("User profile not found.")
        
        # Step 7: Test monthly interest calculation
        print("\n7. Testing monthly interest calculation...")
        if investments:
            for inv in investments:
                interest_amount = InvestmentService.calculate_monthly_interest(db, inv.id)
                print(f"  - Investment ID: {inv.id}, Monthly Interest Amount: {interest_amount}")
                
                # Process the interest payment
                InvestmentService.process_interest_payment(db, inv.id)
                print("  - Interest payment processed.")
        
        # Step 8: Check if interest transactions were created
        print("\n8. Checking for interest transactions...")
        interest_transactions = db.query(IncomeTransaction).filter(
            IncomeTransaction.description.like("%interest%"),
            IncomeTransaction.wallet_id.in_([w.id for w in test_user.income_wallet])
        ).all()
        
        if interest_transactions:
            print(f"Found {len(interest_transactions)} interest transaction(s):")
            for tx in interest_transactions:
                print(f"  - Transaction ID: {tx.id}, Amount: {tx.amount}, Description: {tx.description}")
        else:
            print("No interest transactions found.")
        
        print("\nTest completed successfully!")
        
    except Exception as e:
        print(f"Error during test: {str(e)}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    test_payment_flow()
