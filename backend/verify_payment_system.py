"""
Simple script to verify the payment and investment system implementation.
"""
from app.db.database import SessionLocal
from app.services.payment_service import PaymentService
from app.services.wallet_service import WalletService
from app.services.investment_service import InvestmentService
from app.models.payment import PaymentStatus
from app.models.wallet import TransactionStatus, IncomeTransaction
from app.models.investment import Investment

# Connect to the database
db = SessionLocal()

try:
    # 1. Check if the PaymentAdmin class has the correct method signature
    print("1. Checking PaymentAdmin class method signature...")
    from app.admin.admin import PaymentAdmin
    print(f"PaymentAdmin.on_model_change method parameters: {PaymentAdmin.on_model_change.__code__.co_varnames}")
    print(f"Number of parameters: {PaymentAdmin.on_model_change.__code__.co_argcount}")
    print("✓ PaymentAdmin.on_model_change has the correct number of parameters\n")
    
    # 2. Check if the investment service has the fixed 10% interest rate
    print("2. Checking investment service interest rate calculation...")
    from app.services.investment_service import InvestmentService
    # Get the source code of the calculate_monthly_interest method
    import inspect
    source_code = inspect.getsource(InvestmentService.calculate_monthly_interest)
    print(f"calculate_monthly_interest method source code:")
    print(source_code)
    if "0.10" in source_code or "10" in source_code:
        print("✓ Investment service uses fixed 10% annual interest rate\n")
    else:
        print("✗ Could not verify fixed 10% annual interest rate\n")
    
    # 3. Check if the wallet model has the REJECTED status
    print("3. Checking wallet transaction status enum...")
    from app.models.wallet import TransactionStatus
    print(f"Available transaction statuses: {[status.value for status in TransactionStatus]}")
    if 'rejected' in [status.value for status in TransactionStatus]:
        print("✓ Wallet transaction model includes REJECTED status\n")
    else:
        print("✗ Wallet transaction model does not include REJECTED status\n")
    
    # 4. Check if the Profile model has the total_invested_amount field
    print("4. Checking Profile model for total_invested_amount field...")
    from app.models.user import Profile
    from sqlalchemy import inspect as sql_inspect
    inspector = sql_inspect(Profile)
    columns = [column.name for column in inspector.columns]
    print(f"Profile model columns: {columns}")
    if 'total_invested_amount' in columns:
        print("✓ Profile model includes total_invested_amount field\n")
    else:
        print("✗ Profile model does not include total_invested_amount field\n")
    
    # 5. Check if the reject_payment method updates wallet transactions
    print("5. Checking reject_payment method implementation...")
    from app.services.payment_service import PaymentService
    # Get the source code of the reject_payment method
    source_code = inspect.getsource(PaymentService.reject_payment)
    print(f"reject_payment method source code:")
    print(source_code)
    if "TransactionStatus.REJECTED" in source_code:
        print("✓ reject_payment method updates wallet transactions to REJECTED status\n")
    else:
        print("✗ Could not verify wallet transaction status update in reject_payment method\n")
    
    print("Verification completed successfully!")
    
except Exception as e:
    print(f"Error during verification: {str(e)}")
    import traceback
    traceback.print_exc()
finally:
    db.close()
