from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.api.deps import get_current_user
from app.models.user import User
from app.schemas.payment import WalletResponse, DepositRequest
from app.services.payment import get_or_create_wallet, deposit_funds, PaymentException

router = APIRouter(prefix="/wallet", tags=["Wallet"])

@router.get("/me", response_model=WalletResponse)
def get_my_wallet(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Retrieve the current user's simulated digital wallet balance."""
    wallet = get_or_create_wallet(db, current_user.id)
    return wallet

@router.post("/deposit", response_model=WalletResponse)
def deposit_to_wallet(
    payload: DepositRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Deposit simulation funds into the current user's wallet for testing."""
    try:
        wallet = deposit_funds(db, current_user.id, payload.amount)
        return wallet
    except PaymentException as exc:
        raise HTTPException(status_code=exc.status_code, detail=exc.message)
