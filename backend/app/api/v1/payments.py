from typing import Optional
from math import ceil
from fastapi import APIRouter, Depends, HTTPException, Query, Request, status

from sqlalchemy.orm import Session
from app.core.database import get_db
from app.api.deps import get_current_user
from app.models.user import User
from app.schemas.payment import (
    TransferRequest,
    TransactionResponse,
    TransactionDetailResponse,
    XAIExplanationResponse,
    PaginatedTransactionHistory,
)

from app.services.payment import (
    execute_p2p_transfer,
    get_transaction_history,
    get_transaction_by_id,
    PaymentException,
)

router = APIRouter(prefix="/payments", tags=["Payments"])

@router.post("/transfer", response_model=TransactionResponse, status_code=status.HTTP_201_CREATED)
def transfer(
    payload: TransferRequest,
    request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Execute a peer-to-peer digital wallet transfer to another user.
    Uses row-level pessimistic locking and triggers risk evaluation hook.
    """
    if not payload.recipient_email and not payload.recipient_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Either recipient_email or recipient_id must be provided"
        )

    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        client_ip = forwarded.split(",")[0].strip()
    else:
        client_ip = request.client.host if request.client else "0.0.0.0"


    try:
        tx = execute_p2p_transfer(
            db=db,
            sender_id=current_user.id,
            amount=payload.amount,
            recipient_email=payload.recipient_email,
            recipient_id=payload.recipient_id,
            note=payload.note,
            client_ip=client_ip,
        )
        return tx
    except PaymentException as exc:
        raise HTTPException(status_code=exc.status_code, detail=exc.message)

@router.get("/history", response_model=PaginatedTransactionHistory)
def get_history(
    page: int = Query(1, ge=1, description="Page number"),
    size: int = Query(10, ge=1, le=100, description="Items per page"),
    direction: Optional[str] = Query("all", description="Filter by direction: all, sent, received"),
    status: Optional[str] = Query(None, description="Filter by status: APPROVED, PENDING, FLAGGED, BLOCKED, FAILED"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Retrieve paginated transaction history for the current user."""
    items, total = get_transaction_history(
        db=db,
        user_id=current_user.id,
        page=page,
        size=size,
        direction=direction,
        status=status,
    )

    pages = ceil(total / size) if size > 0 else 0
    return PaginatedTransactionHistory(
        total=total,
        page=page,
        size=size,
        pages=pages,
        items=items,
    )

@router.get("/{transaction_id}", response_model=TransactionDetailResponse)
def get_transaction_detail(
    transaction_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Retrieve details for a single transaction by ID or reference ID."""
    tx = get_transaction_by_id(db, transaction_id)
    if not tx:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Transaction not found"
        )

    # Authorization check: user must be sender or recipient (or admin)
    if current_user.id not in [tx.sender_id, tx.recipient_id] and current_user.role != "ADMIN":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied to transaction details"
        )

    response_data = TransactionDetailResponse.model_validate(tx)
    if tx.sender:
        response_data.sender_email = tx.sender.email
        response_data.sender_name = tx.sender.full_name
    if tx.recipient:
        response_data.recipient_email = tx.recipient.email
        response_data.recipient_name = tx.recipient.full_name

    return response_data

@router.get("/{transaction_id}/xai", response_model=XAIExplanationResponse)
def get_transaction_xai_explanation(
    transaction_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Retrieve Explainable AI (XAI) feature attribution breakdown for a transaction."""
    import json
    tx = get_transaction_by_id(db, transaction_id)
    if not tx:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Transaction not found"
        )

    if current_user.id not in [tx.sender_id, tx.recipient_id] and current_user.role != "ADMIN":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied to transaction XAI details"
        )

    parsed_factors = []
    if tx.risk_factors:
        try:
            parsed_factors = json.loads(tx.risk_factors)
        except Exception:
            parsed_factors = []

    rules_score = sum(f.get("impact", 0.0) for f in parsed_factors if f.get("factor_type") == "RULE")
    ml_factors = [f.get("impact", 0.0) for f in parsed_factors if f.get("factor_type") == "ML_ANOMALY"]
    ml_score = ml_factors[0] if ml_factors else 0.0

    action = "APPROVE"
    if tx.status == "BLOCKED":
        action = "BLOCK"
    elif tx.status == "FLAGGED":
        action = "FLAG"

    summary = f"Transaction evaluated with risk score {tx.risk_score:.1f}/100 ({tx.risk_level}). Action taken: {action}."

    return XAIExplanationResponse(
        transaction_id=tx.id,
        reference_id=tx.reference_id,
        amount=tx.amount,
        status=tx.status,
        risk_score=tx.risk_score or 0.0,
        risk_level=tx.risk_level or "LOW",
        action=action,
        rules_score=rules_score,
        ml_score=ml_score,
        risk_factors=parsed_factors,
        explanation_summary=summary
    )

