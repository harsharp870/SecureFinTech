import pytest
from app.services.audit_service import log_audit_event, get_audit_logs
from app.models.audit import AuditCategory, AuditSeverity

def test_log_and_get_audit_events(db):
    # Log 2 audit events
    log_audit_event(
        db=db,
        action="LOGIN_FAILED",
        category=AuditCategory.SECURITY_EVENT.value,
        severity=AuditSeverity.WARNING.value,
        ip_address="192.168.1.100",
        details={"reason": "Invalid password"}
    )
    log_audit_event(
        db=db,
        action="PASSWORD_CHANGED",
        category=AuditCategory.ADMIN_ACTION.value,
        severity=AuditSeverity.INFO.value,
        ip_address="192.168.1.101",
        details={"admin": "system"}
    )

    items, total = get_audit_logs(db, page=1, size=10)
    assert total >= 2

    # Filter by category
    items_sec, total_sec = get_audit_logs(db, category=AuditCategory.SECURITY_EVENT.value)
    assert total_sec >= 1
    assert any(i.action == "LOGIN_FAILED" for i in items_sec)
