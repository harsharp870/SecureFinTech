import uuid
import pytest
from decimal import Decimal
from app.models.user import User, UserRole
from app.models.payment import TransactionStatus, Wallet
from app.services.fraud_engine.feature_extractor import TransactionFeatureVector
from app.services.fraud_engine.ml_detector import MLAnomalyDetector
from app.services.fraud_engine.hybrid_aggregator import HybridFraudAggregator
from app.services.payment import get_or_create_wallet, execute_p2p_transfer
from app.core.security import hash_password, create_access_token

def test_ml_detector_initialization():
    detector = MLAnomalyDetector()
    assert detector.model is not None

    features_normal = TransactionFeatureVector(amount=50.0, velocity_5m=0, seconds_since_last_tx=7200.0, balance_ratio=0.01, hour_of_day=14)
    normal_score = detector.predict_risk_score(features_normal)
    assert 0.0 <= normal_score <= 50.0

def test_hybrid_aggregator_critical_override():
    aggregator = HybridFraudAggregator()

    # Normal transaction
    feat_normal = TransactionFeatureVector(amount=100.0, velocity_5m=0, seconds_since_last_tx=3600.0, balance_ratio=0.01, hour_of_day=12)
    res_normal = aggregator.evaluate_transaction(feat_normal)
    assert res_normal.action == "APPROVE"
    assert res_normal.risk_level in ["LOW", "MEDIUM"]

    # Critical $12,000 transaction
    feat_critical = TransactionFeatureVector(amount=12000.0, velocity_5m=0, seconds_since_last_tx=3600.0, balance_ratio=0.8, hour_of_day=12)
    res_critical = aggregator.evaluate_transaction(feat_critical)
    assert res_critical.action == "BLOCK"
    assert res_critical.risk_level == "CRITICAL"
    assert res_critical.final_risk_score >= 85.0

def test_end_to_end_payment_blocking(client, db):
    uid1 = uuid.uuid4().hex[:8]
    uid2 = uuid.uuid4().hex[:8]

    sender = User(
        email=f"sender_{uid1}@example.com",
        hashed_password=hash_password("Password123!"),
        full_name="Rich Sender",
        role=UserRole.USER
    )
    recipient = User(
        email=f"recipient_{uid2}@example.com",
        hashed_password=hash_password("Password123!"),
        full_name="Recipient User",
        role=UserRole.USER
    )
    db.add_all([sender, recipient])
    db.commit()

    # Fund sender with $50,000 for high-value transfer test
    sender_wallet = get_or_create_wallet(db, sender.id)
    sender_wallet.balance = Decimal("50000.00")
    recipient_wallet = get_or_create_wallet(db, recipient.id)
    db.commit()

    token = create_access_token(sender.id)
    headers = {"Authorization": f"Bearer {token}"}

    # Attempt $12,000 transfer -> Should be BLOCKED
    payload = {
        "recipient_email": recipient.email,
        "amount": 12000.00,
        "note": "Blocked high-value transfer"
    }

    res = client.post("/api/v1/payments/transfer", json=payload, headers=headers)
    assert res.status_code == 201
    data = res.json()
    assert data["status"] == "BLOCKED"
    assert data["risk_level"] == "CRITICAL"
    assert data["risk_score"] >= 85.0

    # Verify sender balance remained unchanged ($50,000)
    db.refresh(sender_wallet)
    assert sender_wallet.balance == Decimal("50000.00")

    # Fetch XAI explanation endpoint
    tx_id = data["id"]
    res_xai = client.get(f"/api/v1/payments/{tx_id}/xai", headers=headers)
    assert res_xai.status_code == 200
    xai_data = res_xai.json()
    assert xai_data["action"] == "BLOCK"
    assert len(xai_data["risk_factors"]) >= 1
    assert "CRITICAL" in xai_data["explanation_summary"]
