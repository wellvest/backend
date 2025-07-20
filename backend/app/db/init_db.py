from sqlalchemy.orm import Session
from app.core.auth import get_password_hash
from app.models.user import User, Profile, Address, BankDetail
from app.models.wallet import IncomeWallet, ShoppingWallet
from app.models.network import Network
import uuid

# Initial demo data
def init_db(db: Session) -> None:
    """Initialize the database with demo data."""
    # Check if we already have users
    user = db.query(User).first()
    if user:
        return  # Database already initialized
    
    # Create demo user
    demo_user = User(
        id=str(uuid.uuid4()),
        member_id="10101631",
        name="MOHD INAM",
        email="mohdinam@example.com",
        hashed_password=get_password_hash("password123"),
        phone="9997338564",
        date_of_birth="01/01/1963",
        gender="Male",
        avatar="/api/placeholder/100/100"
    )
    db.add(demo_user)
    db.flush()
    
    # Create profile
    profile = Profile(
        user_id=demo_user.id,
        plan_amount=50000.0,
        kyc_verified=True
    )
    db.add(profile)
    
    # Create address
    address = Address(
        user_id=demo_user.id,
        address_type="home",
        address_line1="123 Main Street",
        address_line2="Apartment 4B",
        city="delhi",
        state="Delhi",
        zip_code="100001",
        country="india",
        notes="Near the community center",
        is_default=True
    )
    db.add(address)
    
    # Create bank details
    bank_detail = BankDetail(
        user_id=demo_user.id,
        account_holder_name="MOHD INAM",
        account_number="1234567890",
        bank_name="State Bank of India",
        branch_name="delhi Main",
        ifsc_code="SBIN0001234",
        is_default=True
    )
    db.add(bank_detail)
    
    # Create wallets
    income_wallet = IncomeWallet(
        user_id=demo_user.id,
        balance=10000.0
    )
    db.add(income_wallet)
    
    shopping_wallet = ShoppingWallet(
        user_id=demo_user.id,
        balance=5000.0
    )
    db.add(shopping_wallet)
    
    # Create network
    network = Network(
        user_id=demo_user.id,
        referral_code=f"REF-{demo_user.member_id}-DEMO",
        total_members=0
    )
    db.add(network)
    
    db.commit()
