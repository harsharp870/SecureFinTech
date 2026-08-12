import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime, ForeignKey
from app.core.database import Base

class LoginAttempt(Base):
    __tablename__ = "login_attempts"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=True)
    email = Column(String(255), nullable=False, index=True)
    ip_address = Column(String(45), nullable=True)
    success = Column(String(10), nullable=False)  # "success" | "failure"
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)
    failure_reason = Column(String(255), nullable=True)
