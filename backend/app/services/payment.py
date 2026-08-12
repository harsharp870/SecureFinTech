from decimal import Decimal
from typing import Optional, List, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import or_, and_, desc
from app.models.user import User
from app.models.payment import Wallet, Transaction, TransactionStatus
from app.services.fraud_evaluator import BaseFraudEvaluator, default_fraud_evaluator

class PaymentException(Exception):
    def __init__(self, message: str, status_code: int = 400):
        self.message = message
        self.status_code = status_code
        super().__init__(message)

def get_or_create_wallet(db: Session, user_id: str) -> Wallet:
    """Returns user's wallet, initializing with default 10,000.00 USD balance if not present."""
    wallet = db.query(Wallet).filter(Wallet.user_id == user_id).first()
    if not wallet:
        wallet = Wallet(user_id=user_id, balance=Decimal("10000.00"), currency="USD")
        db.add(wallet)
        db.commit()
        db.refresh(wallet)
    return wallet

def deposit_funds(db: Session, user_id: str, amount: Decimal) -> Wallet:
    """Deposits simulation funds into the user's wallet."""
    if amount <= Decimal("0"):
        raise PaymentException("Deposit amount must be greater than zero", status_code=400)

    wallet = get_or_create_wallet(db, user_id)

    # Apply row-level lock if supported
    if db.bind.dialect.name != "sqlite":
        wallet = db.query(Wallet).filter(Wallet.id == wallet.id).with_for_update().first()

    wallet.balance += amount
    db.commit()
    db.refresh(wallet)
    return wallet

def execute_p2p_transfer(
    db: Session,
    sender_id: str,
    amount: Decimal,
    recipient_email: Optional[str] = None,
    recipient_id: Optional[str] = None,
    note: Optional[str] = None,
    client_ip: Optional[str] = None,
    evaluator: BaseFraudEvaluator = default_fraud_evaluator
) -> Transaction:
    """
    Executes an atomic peer-to-peer transfer between users.
    Enforces row-level pessimistic locking ordered by user_id to prevent deadlocks.
    """
    if amount <= Decimal("0"):
        raise PaymentException("Transfer amount must be greater than zero", status_code=400)

    # 1. Resolve recipient user
    recipient: Optional[User] = None
    if recipient_id:
        recipient = db.query(User).filter(User.id == recipient_id).first()
    elif recipient_email:
        recipient = db.query(User).filter(User.email == recipient_email).first()

    if not recipient:
        raise PaymentException("Recipient user not found", status_code=404)

    if recipient.id == sender_id:
        raise PaymentException("Self-transfers are not allowed", status_code=400)

    if not recipient.is_active or recipient.is_locked:
        raise PaymentException("Recipient account is inactive or locked", status_code=400)

    # 2. Acquire row-level locks on both wallets in deterministic sorted order
    sorted_user_ids = sorted([sender_id, recipient.id])
    
    # Ensure wallets exist for both users first
    get_or_create_wallet(db, sender_id)
    get_or_create_wallet(db, recipient.id)

    wallet_query = db.query(Wallet).filter(Wallet.user_id.in_(sorted_user_ids))
    if db.bind.dialect.name != "sqlite":
        wallet_query = wallet_query.with_for_update()

    wallets = wallet_query.all()
    wallet_map = {w.user_id: w for w in wallets}

    sender_wallet = wallet_map.get(sender_id)
    recipient_wallet = wallet_map.get(recipient.id)

    if not sender_wallet or not recipient_wallet:
        raise PaymentException("Wallet initialization error", status_code=500)

    if sender_wallet.balance < amount:
        raise PaymentException("Insufficient wallet balance", status_code=400)

    # 3. Create Transaction in PENDING status
    tx = Transaction(
        sender_id=sender_id,
        recipient_id=recipient.id,
        amount=amount,
        currency="USD",
        status=TransactionStatus.PENDING,
        note=note
    )
    db.add(tx)
    db.flush()  # Populates tx.id and reference_id

    # 4. Evaluate transaction via FraudEvaluator hook
    try:
        eval_result = evaluator.evaluate(db, tx, client_ip=client_ip)
    except TypeError:
        eval_result = evaluator.evaluate(db, tx)

    tx.risk_score = eval_result.risk_score
    tx.risk_level = eval_result.risk_level
    tx.risk_factors = eval_result.risk_factors



    if eval_result.decision == "APPROVE":
        sender_wallet.balance -= amount
        recipient_wallet.balance += amount
        tx.status = TransactionStatus.APPROVED
    elif eval_result.decision == "FLAG":
        tx.status = TransactionStatus.FLAGGED
        tx.failure_reason = "Flagged for manual security review"
    else:
        tx.status = TransactionStatus.BLOCKED
        tx.failure_reason = "Blocked by automated security risk evaluation"

    db.commit()
    db.refresh(tx)
    return tx

def get_transaction_history(
    db: Session,
    user_id: str,
    page: int = 1,
    size: int = 10,
    direction: Optional[str] = "all",
    status: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None
) -> Tuple[List[Transaction], int]:
    """Returns paginated transactions for the specified user with optional filters."""
    query = db.query(Transaction)

    if direction == "sent":
        query = query.filter(Transaction.sender_id == user_id)
    elif direction == "received":
        query = query.filter(Transaction.recipient_id == user_id)
    else:
        query = query.filter(or_(Transaction.sender_id == user_id, Transaction.recipient_id == user_id))

    if status:
        query = query.filter(Transaction.status == status.upper())

    total = query.count()
    offset = (page - 1) * size
    items = query.order_by(desc(Transaction.created_at)).offset(offset).limit(size).all()

    return items, total

def get_transaction_by_id(db: Session, transaction_id: str) -> Optional[Transaction]:
    """Retrieves a single transaction by ID or reference_id."""
    return db.query(Transaction).filter(
        or_(Transaction.id == transaction_id, Transaction.reference_id == transaction_id)
    ).first()
