import uuid
import pytest
from app.models.user import User, UserRole
from app.core.security import hash_password, create_access_token
from app.services.audit_service import log_audit_event

def test_admin_audit_logs_rbac_and_query(client, db):
    uid_user = uuid.uuid4().hex[:8]
    uid_admin = uuid.uuid4().hex[:8]

    normal_user = User(
        email=f"user_{uid_user}@example.com",
        hashed_password=hash_password("Password123!"),
        full_name="Normal User",
        role=UserRole.USER
    )
    admin_user = User(
        email=f"admin_{uid_admin}@example.com",
        hashed_password=hash_password("Password123!"),
        full_name="Admin Security Officer",
        role=UserRole.ADMIN
    )
    db.add_all([normal_user, admin_user])
    db.commit()

    log_audit_event(
        db=db,
        action="TEST_ADMIN_ACTION",
        category="ADMIN_ACTION",
        severity="INFO",
        actor_id=admin_user.id,
        details={"test": "ok"}
    )

    # 1. Non-admin access should return HTTP 403 FORBIDDEN
    user_token = create_access_token(normal_user.id)
    user_headers = {"Authorization": f"Bearer {user_token}"}
    res_forbidden = client.get("/api/v1/admin/audit-logs", headers=user_headers)
    assert res_forbidden.status_code == 403

    # 2. Admin access should return HTTP 200 OK with audit logs list
    admin_token = create_access_token(admin_user.id)
    admin_headers = {"Authorization": f"Bearer {admin_token}"}
    res_ok = client.get("/api/v1/admin/audit-logs", headers=admin_headers)
    assert res_ok.status_code == 200
    data = res_ok.json()
    assert data["total"] >= 1
    assert any(item["action"] == "TEST_ADMIN_ACTION" for item in data["items"])
