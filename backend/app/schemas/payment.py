from pydantic import BaseModel, Field, EmailStr, ConfigDict
from typing import Optional, List
from datetime import datetime
from decimal import Decimal
from app.models.payment import TransactionStatus

class WalletResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    user_id: str
    balance: Decimal
    currency: str
    created_at: datetime
    updated_at: datetime

class DepositRequest(BaseModel):
    amount: Decimal = Field(..., gt=0, max_digits=12, decimal_places=2, description="Amount to deposit, must be > 0")

class TransferRequest(BaseModel):
    recipient_email: Optional[EmailStr] = None
    recipient_id: Optional[str] = None
    amount: Decimal = Field(..., gt=0, max_digits=12, decimal_places=2, description="Transfer amount, must be > 0")
    note: Optional[str] = Field(None, max_length=255)

class TransactionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    reference_id: str
    sender_id: str
    recipient_id: str
    amount: Decimal
    currency: str
    status: TransactionStatus
    risk_score: Optional[float] = 0.0
    risk_level: Optional[str] = "LOW"
    risk_factors: Optional[str] = None
    failure_reason: Optional[str] = None
    note: Optional[str] = None
    created_at: datetime
    updated_at: datetime

class TransactionDetailResponse(TransactionResponse):
    sender_email: Optional[str] = None
    sender_name: Optional[str] = None
    recipient_email: Optional[str] = None
    recipient_name: Optional[str] = None

class XAIRiskFactorItem(BaseModel):
    factor_type: str
    rule_name: str
    impact: float
    is_critical: bool
    description: str

class XAIExplanationResponse(BaseModel):
    transaction_id: str
    reference_id: str
    amount: Decimal
    status: TransactionStatus
    risk_score: float
    risk_level: str
    action: str
    rules_score: float
    ml_score: float
    risk_factors: List[XAIRiskFactorItem]
    explanation_summary: str


class PaginatedTransactionHistory(BaseModel):
    total: int
    page: int
    size: int
    pages: int
    items: List[TransactionResponse]
