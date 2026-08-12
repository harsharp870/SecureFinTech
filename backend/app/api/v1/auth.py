from datetime import datetime, timedelta
from typing import Optional

import jwt
from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.database import get_db
from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    hash_password,
    verify_password,
)
from app.models.login_attempt import LoginAttempt
from app.models.user import User, UserRole
from app.schemas.auth import (
    LoginRequest,
    RefreshRequest,
    SignupRequest,
    TokenResponse,
)
from app.schemas.user import UserPublic
from app.api.deps import get_current_user

router = APIRouter(prefix="/auth", tags=["Authentication"])


def _get_client_ip(request: Request) -> str:
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.client.host if request.client else "unknown"


def _record_attempt(
    db: Session,
    email: str,
    success: bool,
    ip: str,
    user_id: Optional[str] = None,
    reason: Optional[str] = None,
):
    attempt = LoginAttempt(
        user_id=user_id,
        email=email,
        ip_address=ip,
        success="success" if success else "failure",
        failure_reason=reason,
    )
    db.add(attempt)
    db.commit()


@router.post("/signup", response_model=UserPublic, status_code=status.HTTP_201_CREATED)
def signup(payload: SignupRequest, db: Session = Depends(get_db)):
    """Register a new user account."""
    existing = db.query(User).filter(User.email == payload.email).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email already registered",
        )
    user = User(
        email=payload.email,
        hashed_password=hash_password(payload.password),
        full_name=payload.full_name,
        role=UserRole.USER,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@router.post("/login", response_model=TokenResponse)
def login(payload: LoginRequest, request: Request, db: Session = Depends(get_db)):
    """Authenticate a user and return JWT access + refresh tokens."""
    ip = _get_client_ip(request)
    user = db.query(User).filter(User.email == payload.email).first()

    if not user:
        _record_attempt(db, payload.email, False, ip, reason="user_not_found")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
        )

    # Check account lockout
    if user.is_locked and user.locked_until:
        if datetime.utcnow() < user.locked_until:
            remaining = int((user.locked_until - datetime.utcnow()).total_seconds() / 60)
            raise HTTPException(
                status_code=status.HTTP_423_LOCKED,
                detail=f"Account locked. Try again in {remaining} minute(s).",
            )
        else:
            # Lockout period expired — unlock
            user.is_locked = False
            user.failed_login_attempts = 0
            user.locked_until = None
            db.commit()

    if not verify_password(payload.password, user.hashed_password):
        user.failed_login_attempts += 1
        if user.failed_login_attempts >= settings.MAX_FAILED_LOGIN_ATTEMPTS:
            user.is_locked = True
            user.locked_until = datetime.utcnow() + timedelta(
                minutes=settings.ACCOUNT_LOCKOUT_MINUTES
            )
            db.commit()
            _record_attempt(db, payload.email, False, ip, user_id=user.id, reason="account_locked")
            raise HTTPException(
                status_code=status.HTTP_423_LOCKED,
                detail=f"Too many failed attempts. Account locked for {settings.ACCOUNT_LOCKOUT_MINUTES} minutes.",
            )
        db.commit()
        _record_attempt(db, payload.email, False, ip, user_id=user.id, reason="wrong_password")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account deactivated",
        )

    # Successful login — reset counters
    user.failed_login_attempts = 0
    user.is_locked = False
    user.locked_until = None
    db.commit()

    _record_attempt(db, payload.email, True, ip, user_id=user.id)
    return TokenResponse(
        access_token=create_access_token(user.id),
        refresh_token=create_refresh_token(user.id),
    )


@router.post("/refresh", response_model=TokenResponse)
def refresh_token(payload: RefreshRequest, db: Session = Depends(get_db)):
    """Issue a new access token using a valid refresh token."""
    try:
        token_data = decode_token(payload.refresh_token)
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Refresh token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token")

    if token_data.get("type") != "refresh":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token type")

    user_id = token_data.get("sub")
    user = db.query(User).filter(User.id == user_id).first()
    if not user or not user.is_active:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found or inactive")

    return TokenResponse(
        access_token=create_access_token(user.id),
        refresh_token=create_refresh_token(user.id),
    )


@router.get("/me", response_model=UserPublic)
def get_me(current_user: User = Depends(get_current_user)):
    """Return the currently authenticated user's profile."""
    return current_user
