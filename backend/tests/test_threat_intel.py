import uuid
import pytest
from decimal import Decimal
from app.models.user import User, UserRole
from app.services.threat_intel import ThreatIntelService
from app.services.payment import get_or_create_wallet
from app.core.security import hash_password, create_access_token

def test_threat_intel_service_lookup():
    service = ThreatIntelService()

    # Clean IP
    res_clean = service.evaluate_ip("192.168.1.50")
    assert not res_clean.is_malicious
    assert res_clean.threat_score == 0.0

    # Tor Exit Node IP (185.220.101.5)
    res_tor = service.evaluate_ip("185.220.101.5")
    assert res_tor.is_malicious
    assert res_tor.threat_score == 90.0
    assert res_tor.threat_category == "TOR_EXIT_NODE"

def test_threat_intel_automated_payment_blocking(client, db):
    uid1 = uuid.uuid4().hex[:8]
    uid2 = uuid.uuid4().hex[:8]

    sender = User(
        email=f"tor_user_{uid1}@example.com",
        hashed_password=hash_password("Password123!"),
        full_name="Tor Sender",
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

    get_or_create_wallet(db, sender.id)
    get_or_create_wallet(db, recipient.id)

    token = create_access_token(sender.id)

    # Initiate transfer coming from Tor Exit Node IP (185.220.101.5)
    headers = {
        "Authorization": f"Bearer {token}",
        "X-Forwarded-For": "185.220.101.5"
    }

    payload = {
        "recipient_email": recipient.email,
        "amount": 50.00,
        "note": "Transfer via Tor exit node"
    }

    res = client.post("/api/v1/payments/transfer", json=payload, headers=headers)
    assert res.status_code == 201
    data = res.json()
    assert data["status"] == "BLOCKED"
    assert data["risk_level"] == "CRITICAL"
    assert data["risk_score"] >= 90.0
