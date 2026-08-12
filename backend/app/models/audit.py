import uuid
import enum
from datetime import datetime, timezone
from sqlalchemy import Column, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.core.database import Base

def utc_now():
    return datetime.now(timezone.utc)

class AuditCategory(str, enum.Enum):
    SECURITY_EVENT = "SECURITY_EVENT"
    ADMIN_ACTION = "ADMIN_ACTION"
    SYSTEM_ALERT = "SYSTEM_ALERT"

class AuditSeverity(str, enum.Enum):
    INFO = "INFO"
    WARNING = "WARNING"
    CRITICAL = "CRITICAL"

class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    category = Column(String(50), nullable=False, index=True, default=AuditCategory.SECURITY_EVENT)
    severity = Column(String(20), nullable=False, index=True, default=AuditSeverity.INFO)
    action = Column(String(100), nullable=False, index=True)
    actor_id = Column(String(36), ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)
    ip_address = Column(String(45), nullable=True, index=True)
    user_agent = Column(String(255), nullable=True)
    details = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False, index=True)

    actor = relationship("User", foreign_keys=[actor_id])
