from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from app.models.wallet import TransactionType, TransactionStatus

# Income Wallet Schemas
class IncomeWalletBase(BaseModel):
    balance: float = 0.0

class IncomeWalletCreate(IncomeWalletBase):
    pass

class IncomeWalletUpdate(BaseModel):
    balance: Optional[float] = None

class IncomeWalletResponse(IncomeWalletBase):
    id: str
    user_id: str
    created_at: datetime
    updated_at: datetime
    
    class Config:
        orm_mode = True

# Income Transaction Schemas
class IncomeTransactionBase(BaseModel):
    amount: float
    transaction_type: TransactionType
    status: TransactionStatus = TransactionStatus.PENDING
    description: Optional[str] = None
    reference_id: Optional[str] = None

class IncomeTransactionCreate(IncomeTransactionBase):
    pass

class IncomeTransactionUpdate(BaseModel):
    status: Optional[TransactionStatus] = None
    description: Optional[str] = None

class IncomeTransactionResponse(IncomeTransactionBase):
    id: str
    wallet_id: str
    created_at: datetime
    updated_at: datetime
    
    class Config:
        orm_mode = True

# Shopping Wallet Schemas
class ShoppingWalletBase(BaseModel):
    balance: float = 0.0

class ShoppingWalletCreate(ShoppingWalletBase):
    pass

class ShoppingWalletUpdate(BaseModel):
    balance: Optional[float] = None

class ShoppingWalletResponse(ShoppingWalletBase):
    id: str
    user_id: str
    created_at: datetime
    updated_at: datetime
    
    class Config:
        orm_mode = True

# Shopping Transaction Schemas
class ShoppingTransactionBase(BaseModel):
    amount: float
    transaction_type: TransactionType
    status: TransactionStatus = TransactionStatus.PENDING
    description: Optional[str] = None
    reference_id: Optional[str] = None

class ShoppingTransactionCreate(ShoppingTransactionBase):
    pass

class ShoppingTransactionUpdate(BaseModel):
    status: Optional[TransactionStatus] = None
    description: Optional[str] = None

class ShoppingTransactionResponse(ShoppingTransactionBase):
    id: str
    wallet_id: str
    created_at: datetime
    updated_at: datetime
    
    class Config:
        orm_mode = True

# Shopping Voucher Schemas
class ShoppingVoucherBase(BaseModel):
    code: str
    amount: float
    expiry_date: Optional[datetime] = None

class ShoppingVoucherCreate(ShoppingVoucherBase):
    pass

class ShoppingVoucherUpdate(BaseModel):
    is_used: Optional[bool] = None
    used_at: Optional[datetime] = None

class ShoppingVoucherResponse(ShoppingVoucherBase):
    id: str
    wallet_id: str
    is_used: bool
    created_at: datetime
    used_at: Optional[datetime] = None
    
    class Config:
        orm_mode = True

# Wallet with Transactions Response
class IncomeWalletWithTransactionsResponse(IncomeWalletResponse):
    transactions: List[IncomeTransactionResponse] = []
    
    class Config:
        orm_mode = True

class ShoppingWalletWithTransactionsResponse(ShoppingWalletResponse):
    transactions: List[ShoppingTransactionResponse] = []
    vouchers: List[ShoppingVoucherResponse] = []
    
    class Config:
        orm_mode = True
