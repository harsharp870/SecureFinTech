from typing import Optional
from math import ceil
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.api.deps import get_current_admin_user
from app.models.user import User
from app.schemas.audit import PaginatedAuditLogsResponse
from app.services.audit_service import get_audit_logs

router = APIRouter(prefix="/admin", tags=["Admin & Audit Logs"])

@router.get("/audit-logs", response_model=PaginatedAuditLogsResponse)
def get_audit_trail(
    page: int = Query(1, ge=1, description="Page number"),
    size: int = Query(10, ge=1, le=100, description="Items per page"),
    category: Optional[str] = Query(None, description="Filter by category: SECURITY_EVENT, ADMIN_ACTION, SYSTEM_ALERT"),
    severity: Optional[str] = Query(None, description="Filter by severity: INFO, WARNING, CRITICAL"),
    action: Optional[str] = Query(None, description="Filter by action name"),
    actor_id: Optional[str] = Query(None, description="Filter by actor user ID"),
    admin_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """
    Retrieve paginated audit logs and security events.
    Restricted to Admin users only.
    """
    items, total = get_audit_logs(
        db=db,
        page=page,
        size=size,
        category=category,
        severity=severity,
        action=action,
        actor_id=actor_id,
    )

    pages = ceil(total / size) if size > 0 else 0
    return PaginatedAuditLogsResponse(
        total=total,
        page=page,
        size=size,
        pages=pages,
        items=items,
    )
