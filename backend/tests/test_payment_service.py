from decimal import Decimal
import pytest
from app.models.user import User, UserRole
from app.models.payment import Wallet, Transaction, TransactionStatus
from app.services.payment import (
    get_or_create_wallet,
    deposit_funds,
    execute_p2p_transfer,
    PaymentException,
)
from app.core.security import hash_password

def test_wallet_auto_creation(db):
    user = User(
        email="test_wallet_user@example.com",
        hashed_password=hash_password("Password123!"),
        full_name="Wallet Test User",
        role=UserRole.USER,
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    wallet = get_or_create_wallet(db, user.id)
    assert wallet is not None
    assert wallet.user_id == user.id
    assert wallet.balance == Decimal("10000.00")
    assert wallet.currency == "USD"

def test_deposit_funds(db):
    user = User(
        email="test_deposit_user@example.com",
        hashed_password=hash_password("Password123!"),
        full_name="Deposit User",
        role=UserRole.USER,
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    wallet = deposit_funds(db, user.id, Decimal("500.00"))
    assert wallet.balance == Decimal("10500.00")

def test_successful_p2p_transfer(db):
    sender = User(
        email="sender@example.com",
        hashed_password=hash_password("Password123!"),
        full_name="Sender User",
    )
    recipient = User(
        email="recipient@example.com",
        hashed_password=hash_password("Password123!"),
        full_name="Recipient User",
    )
    db.add_all([sender, recipient])
    db.commit()

    sender_wallet = get_or_create_wallet(db, sender.id)
    recipient_wallet = get_or_create_wallet(db, recipient.id)

    tx = execute_p2p_transfer(
        db,
        sender_id=sender.id,
        recipient_email=recipient.email,
        amount=Decimal("1500.00"),
        note="Dinner split"
    )

    db.refresh(sender_wallet)
    db.refresh(recipient_wallet)

    assert tx.status == TransactionStatus.APPROVED
    assert tx.amount == Decimal("1500.00")
    assert sender_wallet.balance == Decimal("8500.00")
    assert recipient_wallet.balance == Decimal("11500.00")

def test_transfer_insufficient_funds(db):
    sender = User(
        email="poor_sender@example.com",
        hashed_password=hash_password("Password123!"),
        full_name="Poor Sender",
    )
    recipient = User(
        email="rich_recipient@example.com",
        hashed_password=hash_password("Password123!"),
        full_name="Rich Recipient",
    )
    db.add_all([sender, recipient])
    db.commit()

    get_or_create_wallet(db, sender.id)
    get_or_create_wallet(db, recipient.id)

    with pytest.raises(PaymentException) as exc_info:
        execute_p2p_transfer(
            db,
            sender_id=sender.id,
            recipient_email=recipient.email,
            amount=Decimal("50000.00")
        )
    assert "Insufficient wallet balance" in str(exc_info.value)

def test_transfer_self_transfer_prevented(db):
    sender = User(
        email="self_user@example.com",
        hashed_password=hash_password("Password123!"),
        full_name="Self User",
    )
    db.add(sender)
    db.commit()

    with pytest.raises(PaymentException) as exc_info:
        execute_p2p_transfer(
            db,
            sender_id=sender.id,
            recipient_id=sender.id,
            amount=Decimal("100.00")
        )
    assert "Self-transfers are not allowed" in str(exc_info.value)
