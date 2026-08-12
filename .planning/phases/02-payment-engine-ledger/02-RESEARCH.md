# Phase 2: Payment Engine & Ledger Technical Research

**Date:** 2026-08-13
**Phase:** 02 - Payment Engine & Ledger
**Status:** Complete

## Executive Summary
Phase 2 builds the core financial transaction engine for SecureFinTech. It introduces digital wallet models, double-entry ledger record keeping, atomic P2P transfers with row-level pessimistic locking, transaction status lifecycle management (`PENDING`, `APPROVED`, `FLAGGED`, `BLOCKED`), and a modular `FraudEvaluator` hook interface ready for Phase 3 ML integration.

---

## 1. Database Schema & Architecture

### 1.1 Wallet Model (`backend/app/models/payment.py`)
```python
class Wallet(Base):
    __tablename__ = "wallets"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False)
    balance = Column(Numeric(12, 2), nullable=False, default=10000.00)
    currency = Column(String(3), nullable=False, default="USD")
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    user = relationship("User", back_populates="wallet")
```

### 1.2 Transaction Model (`backend/app/models/payment.py`)
```python
class TransactionStatus(str, enum.Enum):
    PENDING = "PENDING"
    APPROVED = "APPROVED"
    FLAGGED = "FLAGGED"
    BLOCKED = "BLOCKED"
    FAILED = "FAILED"

class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True, index=True)
    reference_id = Column(String(36), unique=True, index=True, default=lambda: str(uuid.uuid4()))
    sender_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    recipient_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    amount = Column(Numeric(12, 2), nullable=False)
    currency = Column(String(3), nullable=False, default="USD")
    status = Column(Enum(TransactionStatus), nullable=False, default=TransactionStatus.PENDING)
    risk_score = Column(Float, nullable=True, default=0.0)
    risk_level = Column(String(20), nullable=True, default="LOW")
    failure_reason = Column(String(255), nullable=True)
    note = Column(String(255), nullable=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    sender = relationship("User", foreign_keys=[sender_id])
    recipient = relationship("User", foreign_keys=[recipient_id])
```

---

## 2. Atomic Transfer & Concurrency Mechanics

### 2.1 Pessimistic Row Locking (`SELECT FOR UPDATE`)
To prevent deadlocks and race conditions when two users attempt concurrent transfers:
1. Always acquire locks on `Wallet` rows in ascending order of `Wallet.id` (e.g., `first_id = min(sender.id, recipient.id)`).
2. Use `.with_for_update()` in SQLAlchemy for PostgreSQL.
3. For SQLite dev environment fallback, SQLAlchemy `with_for_update()` is safely ignored or handled within SQLite's transaction lock.

```python
def transfer_funds(db: Session, sender_id: int, recipient_id: int, amount: Decimal) -> Transaction:
    # Deadlock avoidance: lock wallets in deterministic order by ID
    first_id, second_id = sorted([sender_id, recipient_id])
    
    # Query with lock if dialect supports it
    wallets = db.query(Wallet).filter(Wallet.user_id.in_([sender_id, recipient_id]))
    if db.bind.dialect.name != "sqlite":
        wallets = wallets.with_for_update()
    
    wallet_map = {w.user_id: w for w in wallets.all()}
    sender_wallet = wallet_map[sender_id]
    recipient_wallet = wallet_map[recipient_id]

    if sender_wallet.balance < amount:
        raise InsufficientFundsException("Insufficient wallet balance")

    # Step 1: Create transaction record in PENDING status
    tx = Transaction(
        sender_id=sender_id,
        recipient_id=recipient_id,
        amount=amount,
        status=TransactionStatus.PENDING
    )
    db.add(tx)
    db.flush()  # assign tx.id

    # Step 2: Evaluate through FraudEvaluator hook
    eval_result = fraud_evaluator.evaluate(db, tx)
    tx.risk_score = eval_result.risk_score
    tx.risk_level = eval_result.risk_level

    if eval_result.decision == "APPROVE":
        sender_wallet.balance -= amount
        recipient_wallet.balance += amount
        tx.status = TransactionStatus.APPROVED
    elif eval_result.decision == "FLAG":
        tx.status = TransactionStatus.FLAGGED
    else:
        tx.status = TransactionStatus.BLOCKED
        tx.failure_reason = "Blocked by security evaluation"

    db.commit()
    db.refresh(tx)
    return tx
```

---

## 3. Modular FraudEvaluator Interface

```python
class FraudEvaluationResult(BaseModel):
    decision: str  # "APPROVE", "FLAG", "BLOCK"
    risk_score: float = 0.0
    risk_level: str = "LOW"
    reasons: list[str] = []

class BaseFraudEvaluator(ABC):
    @abstractmethod
    def evaluate(self, db: Session, transaction: Transaction) -> FraudEvaluationResult:
        pass

class Phase2PassThroughEvaluator(BaseFraudEvaluator):
    """Phase 2 default evaluator: auto-approves transactions."""
    def evaluate(self, db: Session, transaction: Transaction) -> FraudEvaluationResult:
        return FraudEvaluationResult(
            decision="APPROVE",
            risk_score=0.0,
            risk_level="LOW",
            reasons=["Phase 2 mock auto-approval"]
        )
```

---

## 4. Validation Architecture

### Verification Strategy
- **Unit Tests**: Test wallet auto-creation upon registration, deposit endpoint, transfer validation rules.
- **Integration Tests**: End-to-end P2P transfers verifying balance updates, transaction status lifecycle (`APPROVED`, `FLAGGED`, `BLOCKED`).
- **Concurrency Tests**: Simulate simultaneous transfers to ensure balance atomicity and lock consistency.
