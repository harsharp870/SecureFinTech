import json
from typing import Optional, List, Tuple, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import desc
from app.models.audit import AuditLog, AuditCategory, AuditSeverity

def log_audit_event(
    db: Session,
    action: str,
    category: str = AuditCategory.SECURITY_EVENT.value,
    severity: str = AuditSeverity.INFO.value,
    actor_id: Optional[str] = None,
    ip_address: Optional[str] = None,
    user_agent: Optional[str] = None,
    details: Optional[Dict[str, Any]] = None
) -> AuditLog:
    """Atomically records an audit event or security log entry into database."""
    details_str = json.dumps(details) if details else None

    audit_entry = AuditLog(
        category=category,
        severity=severity,
        action=action,
        actor_id=actor_id,
        ip_address=ip_address,
        user_agent=user_agent,
        details=details_str
    )
    db.add(audit_entry)
    db.commit()
    db.refresh(audit_entry)
    return audit_entry

def get_audit_logs(
    db: Session,
    page: int = 1,
    size: int = 10,
    category: Optional[str] = None,
    severity: Optional[str] = None,
    action: Optional[str] = None,
    actor_id: Optional[str] = None
) -> Tuple[List[AuditLog], int]:
    """Retrieves paginated audit log entries with optional filters."""
    query = db.query(AuditLog)

    if category:
        query = query.filter(AuditLog.category == category)
    if severity:
        query = query.filter(AuditLog.severity == severity)
    if action:
        query = query.filter(AuditLog.action == action)
    if actor_id:
        query = query.filter(AuditLog.actor_id == actor_id)

    total = query.count()
    offset = (page - 1) * size
    items = query.order_by(desc(AuditLog.created_at)).offset(offset).limit(size).all()

    return items, total
