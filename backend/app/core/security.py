from datetime import datetime, timedelta
from typing import Any, Optional
import bcrypt
import jwt
from app.core.config import settings


def hash_password(password: str) -> str:
    """Hash a plain-text password using bcrypt directly."""
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode("utf-8"), salt).decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plain-text password against its bcrypt hash."""
    return bcrypt.checkpw(
        plain_password.encode("utf-8"),
        hashed_password.encode("utf-8"),
    )


def _create_token(subject: Any, token_type: str, expires_delta: timedelta) -> str:
    expire = datetime.utcnow() + expires_delta
    payload = {
        "sub": str(subject),
        "type": token_type,
        "exp": expire,
        "iat": datetime.utcnow(),
    }
    return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.JWT_ALGORITHM)


def create_access_token(subject: Any) -> str:
    """Create a short-lived JWT access token."""
    return _create_token(
        subject,
        "access",
        timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES),
    )


def create_refresh_token(subject: Any) -> str:
    """Create a long-lived JWT refresh token."""
    return _create_token(
        subject,
        "refresh",
        timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS),
    )


def decode_token(token: str) -> dict:
    """
    Decode and validate a JWT token.
    Raises jwt.ExpiredSignatureError or jwt.InvalidTokenError on failure.
    """
    return jwt.decode(
        token,
        settings.SECRET_KEY,
        algorithms=[settings.JWT_ALGORITHM],
    )
