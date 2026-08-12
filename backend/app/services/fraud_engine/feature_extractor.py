from dataclasses import dataclass

from datetime import datetime, timezone, timedelta
from typing import List, Optional
from decimal import Decimal
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.models.payment import Transaction, Wallet

@dataclass
class TransactionFeatureVector:
    amount: float
    velocity_5m: int
    seconds_since_last_tx: float
    balance_ratio: float
    hour_of_day: int

    def to_list(self) -> List[float]:
        return [
            self.amount,
            float(self.velocity_5m),
            self.seconds_since_last_tx,
            self.balance_ratio,
            float(self.hour_of_day),
        ]

def extract_feature_vector(
    db: Session,
    sender_id: str,
    amount: Decimal,
    sender_wallet_balance: Decimal
) -> TransactionFeatureVector:
    """Extracts feature vector metrics for risk scoring from DB context."""
    now = datetime.now(timezone.utc)
    five_mins_ago = now - timedelta(minutes=5)

    # 1. Velocity in 5m window
    velocity_5m = db.query(func.count(Transaction.id)).filter(
        Transaction.sender_id == sender_id,
        Transaction.created_at >= five_mins_ago
    ).scalar() or 0

    # 2. Seconds since last transaction
    last_tx = db.query(Transaction).filter(
        Transaction.sender_id == sender_id
    ).order_by(Transaction.created_at.desc()).first()

    seconds_since_last_tx = 86400.0  # Default 24h for first tx
    if last_tx and last_tx.created_at:
        # Handle naive vs aware datetime comparisons safely
        last_time = last_tx.created_at
        if last_time.tzinfo is None:
            last_time = last_time.replace(tzinfo=timezone.utc)
        diff = (now - last_time).total_seconds()
        seconds_since_last_tx = max(0.0, float(diff))

    # 3. Balance ratio
    balance_float = float(sender_wallet_balance) if sender_wallet_balance > 0 else 1.0
    amount_float = float(amount)
    balance_ratio = min(5.0, amount_float / balance_float)

    # 4. Hour of day (UTC)
    hour_of_day = now.hour

    return TransactionFeatureVector(
        amount=amount_float,
        velocity_5m=velocity_5m,
        seconds_since_last_tx=seconds_since_last_tx,
        balance_ratio=balance_ratio,
        hour_of_day=hour_of_day,
    )
