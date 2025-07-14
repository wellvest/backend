from sqladmin import Admin, ModelView
from sqlalchemy.engine import Engine
from sqlalchemy import DateTime
from sqlalchemy.inspection import inspect
from sqlalchemy.orm.relationships import RelationshipProperty

from app.models.user import User, Profile, Address, BankDetail
from app.models.investment import Investment, TeamInvestment, InvestmentStatus
from app.models.plan import Plan
from app.models.wallet import (
    IncomeWallet, ShoppingWallet, IncomeTransaction, ShoppingTransaction,
    ShoppingVoucher, TransactionType, TransactionStatus
)
from app.models.network import Network, Bonus, NOC
from app.models.notification import Notification
from app.admin.auth import get_admin_auth_backend


class BaseModelView(ModelView):
    """Base ModelView class with common configurations for all models"""
    # Override the form creation to handle datetime fields properly
    form_excluded_columns = []
    form_args = {}
    
    async def scaffold_form(self, form_rules=None):
        """Override scaffold_form to exclude datetime fields that should be auto-generated"""
        # Get the default form from the parent class
        form_class = await super().scaffold_form(form_rules)
        
        # Exclude auto-generated datetime fields
        auto_datetime_fields = ['created_at', 'updated_at', 'join_date', 'used_at', 'paid_at']
        
        # Remove fields that should be excluded
        for field_name in auto_datetime_fields:
            if hasattr(form_class, field_name):
                delattr(form_class, field_name)
        
        # Set up datetime fields with proper HTML5 input type
        if hasattr(form_class, '_fields'):
            for field_name, field in form_class._fields.items():
                from wtforms.fields.datetime import DateTimeField
                if isinstance(field, DateTimeField):
                    field.render_kw = {"type": "datetime-local"}
        
        return form_class


class UserAdmin(BaseModelView, model=User):
    name = "User"
    name_plural = "Users"
    icon = "fa-solid fa-user"
    column_list = [User.id, User.name, User.email, User.is_active, User.join_date]
    column_searchable_list = [User.name, User.email, User.member_id]
    column_sortable_list = [User.name, User.email, User.join_date]
    column_details_exclude_list = [User.hashed_password]
    can_create = True
    can_edit = True
    can_delete = True
    can_view_details = True


class ProfileAdmin(BaseModelView, model=Profile):
    name = "Profile"
    name_plural = "Profiles"
    icon = "fa-solid fa-id-card"
    column_list = [Profile.id, Profile.user_id, Profile.plan_amount, Profile.kyc_verified]
    can_create = True
    can_edit = True
    can_delete = True
    can_view_details = True


class AddressAdmin(BaseModelView, model=Address):
    name = "Address"
    name_plural = "Addresses"
    icon = "fa-solid fa-location-dot"
    column_list = [Address.id, Address.user_id, Address.address_type, Address.city, Address.state, Address.country]
    column_searchable_list = [Address.city, Address.state, Address.country]
    can_create = True
    can_edit = True
    can_delete = True
    can_view_details = True


class BankDetailAdmin(BaseModelView, model=BankDetail):
    name = "Bank Detail"
    name_plural = "Bank Details"
    icon = "fa-solid fa-building-columns"
    column_list = [BankDetail.id, BankDetail.user_id, BankDetail.account_holder_name, BankDetail.bank_name]
    column_searchable_list = [BankDetail.account_holder_name, BankDetail.bank_name]
    can_create = True
    can_edit = True
    can_delete = True
    can_view_details = True


class InvestmentAdmin(BaseModelView, model=Investment):
    name = "Investment"
    name_plural = "Investments"
    icon = "fa-solid fa-chart-line"
    column_list = [Investment.id, Investment.user_id, Investment.plan_name, Investment.amount, Investment.status, Investment.start_date]
    column_searchable_list = [Investment.plan_name, Investment.status]
    column_sortable_list = [Investment.amount, Investment.start_date]
    can_create = True
    can_edit = True
    can_delete = True
    can_view_details = True


class TeamInvestmentAdmin(BaseModelView, model=TeamInvestment):
    name = "Team Investment"
    name_plural = "Team Investments"
    icon = "fa-solid fa-users"
    column_list = [TeamInvestment.id, TeamInvestment.investment_id, TeamInvestment.team_member_id, TeamInvestment.amount, TeamInvestment.level]
    can_create = True
    can_edit = True
    can_delete = True
    can_view_details = True


class IncomeWalletAdmin(BaseModelView, model=IncomeWallet):
    name = "Income Wallet"
    name_plural = "Income Wallets"
    icon = "fa-solid fa-wallet"
    column_list = [IncomeWallet.id, IncomeWallet.user_id, IncomeWallet.balance, IncomeWallet.updated_at]
    column_sortable_list = [IncomeWallet.balance, IncomeWallet.updated_at]
    can_create = True
    can_edit = True
    can_delete = True
    can_view_details = True


class IncomeTransactionAdmin(BaseModelView, model=IncomeTransaction):
    name = "Income Transaction"
    name_plural = "Income Transactions"
    icon = "fa-solid fa-money-bill-transfer"
    column_list = [IncomeTransaction.id, IncomeTransaction.wallet_id, IncomeTransaction.amount, IncomeTransaction.transaction_type, IncomeTransaction.status, IncomeTransaction.created_at]
    column_searchable_list = [IncomeTransaction.transaction_type, IncomeTransaction.status]
    column_sortable_list = [IncomeTransaction.amount, IncomeTransaction.created_at]
    can_create = True
    can_edit = True
    can_delete = True
    can_view_details = True


class ShoppingWalletAdmin(BaseModelView, model=ShoppingWallet):
    name = "Shopping Wallet"
    name_plural = "Shopping Wallets"
    icon = "fa-solid fa-cart-shopping"
    column_list = [ShoppingWallet.id, ShoppingWallet.user_id, ShoppingWallet.balance, ShoppingWallet.updated_at]
    column_sortable_list = [ShoppingWallet.balance, ShoppingWallet.updated_at]
    can_create = True
    can_edit = True
    can_delete = True
    can_view_details = True


class ShoppingTransactionAdmin(BaseModelView, model=ShoppingTransaction):
    name = "Shopping Transaction"
    name_plural = "Shopping Transactions"
    icon = "fa-solid fa-receipt"
    column_list = [ShoppingTransaction.id, ShoppingTransaction.wallet_id, ShoppingTransaction.amount, ShoppingTransaction.transaction_type, ShoppingTransaction.status, ShoppingTransaction.created_at]
    column_searchable_list = [ShoppingTransaction.transaction_type, ShoppingTransaction.status]
    column_sortable_list = [ShoppingTransaction.amount, ShoppingTransaction.created_at]
    can_create = True
    can_edit = True
    can_delete = True
    can_view_details = True


class ShoppingVoucherAdmin(BaseModelView, model=ShoppingVoucher):
    name = "Shopping Voucher"
    name_plural = "Shopping Vouchers"
    icon = "fa-solid fa-ticket"
    column_list = [ShoppingVoucher.id, ShoppingVoucher.wallet_id, ShoppingVoucher.code, ShoppingVoucher.amount, ShoppingVoucher.is_used, ShoppingVoucher.expiry_date]
    column_searchable_list = [ShoppingVoucher.code, ShoppingVoucher.is_used]
    column_sortable_list = [ShoppingVoucher.amount, ShoppingVoucher.expiry_date]
    can_create = True
    can_edit = True
    can_delete = True
    can_view_details = True


class NetworkAdmin(BaseModelView, model=Network):
    name = "Network"
    name_plural = "Networks"
    icon = "fa-solid fa-network-wired"
    column_list = [Network.id, Network.user_id, Network.referral_code, Network.referred_by, Network.total_members]
    column_searchable_list = [Network.referral_code]
    column_sortable_list = [Network.total_members]
    can_create = True
    can_edit = True
    can_delete = True
    can_view_details = True


class BonusAdmin(BaseModelView, model=Bonus):
    name = "Bonus"
    name_plural = "Bonuses"
    icon = "fa-solid fa-gift"
    column_list = [Bonus.id, Bonus.user_id, Bonus.amount, Bonus.bonus_type, Bonus.is_paid, Bonus.created_at]
    column_searchable_list = [Bonus.bonus_type, Bonus.is_paid]
    column_sortable_list = [Bonus.amount, Bonus.created_at]
    can_create = True
    can_edit = True
    can_delete = True
    can_view_details = True


class NOCAdmin(BaseModelView, model=NOC):
    name = "NOC"
    name_plural = "NOCs"
    icon = "fa-solid fa-file-contract"
    column_list = [NOC.id, NOC.user_id, NOC.document_url, NOC.issue_date, NOC.expiry_date, NOC.is_active]
    column_searchable_list = [NOC.is_active]
    column_sortable_list = [NOC.issue_date, NOC.expiry_date]
    can_create = True
    can_edit = True
    can_delete = True
    can_view_details = True


class NotificationAdmin(BaseModelView, model=Notification):
    name = "Notification"
    name_plural = "Notifications"
    icon = "fa-solid fa-bell"
    column_list = [Notification.id, Notification.user_id, Notification.title, Notification.type, Notification.read, Notification.created_at]
    column_searchable_list = [Notification.title, Notification.type, Notification.read]
    column_sortable_list = [Notification.created_at]
    can_create = True
    can_edit = True
    can_delete = True
    can_view_details = True


class PlanAdmin(BaseModelView, model=Plan):
    name = "Plan"
    name_plural = "Plans"
    icon = "fa-solid fa-money-bill"
    column_list = [Plan.id, Plan.name, Plan.amount, Plan.duration_months, Plan.interest_rate, Plan.is_active]
    column_searchable_list = [Plan.name]
    column_sortable_list = [Plan.amount, Plan.duration_months, Plan.interest_rate]
    can_create = True
    can_edit = True
    can_delete = True
    can_view_details = True


def setup_admin(app, engine: Engine):
    """Setup the admin interface for the FastAPI application"""
    admin = Admin(
        app, 
        engine,
        title="WellVest Admin",
        authentication_backend=get_admin_auth_backend()
    )
    
    # Register user models
    admin.add_view(UserAdmin)
    admin.add_view(ProfileAdmin)
    admin.add_view(AddressAdmin)
    admin.add_view(BankDetailAdmin)
    
    # Register investment models
    admin.add_view(InvestmentAdmin)
    admin.add_view(TeamInvestmentAdmin)
    
    # Register wallet models
    admin.add_view(IncomeWalletAdmin)
    admin.add_view(IncomeTransactionAdmin)
    admin.add_view(ShoppingWalletAdmin)
    admin.add_view(ShoppingTransactionAdmin)
    admin.add_view(ShoppingVoucherAdmin)
    
    # Register network models
    admin.add_view(NetworkAdmin)
    admin.add_view(BonusAdmin)
    admin.add_view(NOCAdmin)
    
    # Register notification model
    admin.add_view(NotificationAdmin)
    
    # Register plan model
    admin.add_view(PlanAdmin)
    
    return admin
