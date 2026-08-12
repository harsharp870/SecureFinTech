import uuid
import pytest
from decimal import Decimal
from app.models.user import User, UserRole
from app.core.security import hash_password, create_access_token

@pytest.fixture
def auth_users(db):
    uid1 = uuid.uuid4().hex[:8]
    uid2 = uuid.uuid4().hex[:8]

    user1 = User(
        email=f"alice_{uid1}@example.com",
        hashed_password=hash_password("Password123!"),
        full_name="Alice User",
        role=UserRole.USER,
    )
    user2 = User(
        email=f"bob_{uid2}@example.com",
        hashed_password=hash_password("Password123!"),
        full_name="Bob User",
        role=UserRole.USER,
    )
    db.add_all([user1, user2])
    db.commit()
    db.refresh(user1)
    db.refresh(user2)

    token1 = create_access_token(user1.id)
    token2 = create_access_token(user2.id)

    headers1 = {"Authorization": f"Bearer {token1}"}
    headers2 = {"Authorization": f"Bearer {token2}"}

    return {
        "user1": user1,
        "token1": token1,
        "headers1": headers1,
        "user2": user2,
        "token2": token2,
        "headers2": headers2,
    }

def test_get_my_wallet(client, auth_users):
    headers = auth_users["headers1"]
    res = client.get("/api/v1/wallet/me", headers=headers)
    assert res.status_code == 200
    data = res.json()
    assert data["user_id"] == auth_users["user1"].id
    assert float(data["balance"]) == 10000.0
    assert data["currency"] == "USD"

def test_deposit_endpoint(client, auth_users):
    headers = auth_users["headers1"]
    res = client.post("/api/v1/wallet/deposit", json={"amount": 500.00}, headers=headers)
    assert res.status_code == 200
    data = res.json()
    assert float(data["balance"]) == 10500.0

def test_p2p_transfer_endpoint(client, auth_users):
    headers1 = auth_users["headers1"]
    recipient = auth_users["user2"]

    transfer_payload = {
        "recipient_email": recipient.email,
        "amount": 2000.00,
        "note": "Lunch payment"
    }

    res = client.post("/api/v1/payments/transfer", json=transfer_payload, headers=headers1)
    assert res.status_code == 201
    tx_data = res.json()
    assert tx_data["status"] == "APPROVED"
    assert float(tx_data["amount"]) == 2000.00
    assert tx_data["sender_id"] == auth_users["user1"].id
    assert tx_data["recipient_id"] == recipient.id

    # Verify sender balance updated
    res_wallet = client.get("/api/v1/wallet/me", headers=headers1)
    assert float(res_wallet.json()["balance"]) == 8000.0

def test_transaction_history_endpoint(client, auth_users):
    headers1 = auth_users["headers1"]
    headers2 = auth_users["headers2"]
    recipient = auth_users["user2"]

    # Perform transfer
    client.post(
        "/api/v1/payments/transfer",
        json={"recipient_email": recipient.email, "amount": 500.00},
        headers=headers1
    )

    # History for sender (direction=sent)
    res_sent = client.get("/api/v1/payments/history?direction=sent", headers=headers1)
    assert res_sent.status_code == 200
    history_sent = res_sent.json()
    assert history_sent["total"] >= 1
    assert history_sent["items"][0]["sender_id"] == auth_users["user1"].id

    # History for recipient (direction=received)
    res_recv = client.get("/api/v1/payments/history?direction=received", headers=headers2)
    assert res_recv.status_code == 200
    history_recv = res_recv.json()
    assert history_recv["total"] >= 1
    assert history_recv["items"][0]["recipient_id"] == recipient.id

def test_transaction_detail_endpoint(client, auth_users):
    headers1 = auth_users["headers1"]
    headers2 = auth_users["headers2"]
    recipient = auth_users["user2"]

    # Create transfer
    res_tx = client.post(
        "/api/v1/payments/transfer",
        json={"recipient_email": recipient.email, "amount": 750.00},
        headers=headers1
    )
    tx_id = res_tx.json()["id"]

    # Sender detail lookup
    res_detail = client.get(f"/api/v1/payments/{tx_id}", headers=headers1)
    assert res_detail.status_code == 200
    detail = res_detail.json()
    assert detail["id"] == tx_id
    assert detail["sender_email"] == auth_users["user1"].email
    assert detail["recipient_email"] == recipient.email

    # Recipient detail lookup
    res_recv_detail = client.get(f"/api/v1/payments/{tx_id}", headers=headers2)
    assert res_recv_detail.status_code == 200

def test_unauthorized_transaction_detail_lookup(client, db, auth_users):
    headers1 = auth_users["headers1"]
    recipient = auth_users["user2"]

    # Create third user with unique email
    eve_uid = uuid.uuid4().hex[:8]
    unauthorized_user = User(
        email=f"eve_{eve_uid}@example.com",
        hashed_password=hash_password("Password123!"),
        full_name="Eve User",
    )
    db.add(unauthorized_user)
    db.commit()
    token_eve = create_access_token(unauthorized_user.id)
    headers_eve = {"Authorization": f"Bearer {token_eve}"}

    # Perform transfer between user1 and user2
    res_tx = client.post(
        "/api/v1/payments/transfer",
        json={"recipient_email": recipient.email, "amount": 100.00},
        headers=headers1
    )
    tx_id = res_tx.json()["id"]

    # Eve attempts to access transaction details
    res_eve = client.get(f"/api/v1/payments/{tx_id}", headers=headers_eve)
    assert res_eve.status_code == 403
    assert "Access denied" in res_eve.json()["detail"]
