---
phase: 1
slug: foundation-authentication
status: draft
nyquist_compliant: false
wave_0_complete: false
created: 2026-08-13
---

# Phase 1 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | Pytest 8.x + HTTPX (FastAPI TestClient) |
| **Config file** | `backend/pytest.ini` |
| **Quick run command** | `pytest backend/tests/test_auth.py` |
| **Full suite command** | `pytest backend/tests/` |
| **Estimated runtime** | ~5 seconds |

---

## Sampling Rate

- **After every task commit:** Run `pytest backend/tests/test_auth.py`
- **After every plan wave:** Run `pytest backend/tests/`
- **Before `/gsd-verify-work`:** Full suite must be green
- **Max feedback latency:** 10 seconds

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Threat Ref | Secure Behavior | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|------------|-----------------|-----------|-------------------|-------------|--------|
| 01-01-01 | 01 | 1 | AUTH-01 | T-01-01 | User signup hashes password with Argon2/Bcrypt | unit | `pytest backend/tests/test_auth.py -k test_signup` | ❌ W0 | ⬜ pending |
| 01-01-02 | 01 | 1 | AUTH-02 | T-01-02 | Valid credentials return JWT access and refresh tokens | unit | `pytest backend/tests/test_auth.py -k test_login` | ❌ W0 | ⬜ pending |
| 01-02-01 | 02 | 2 | AUTH-03 | T-01-03 | Non-admin user accessing admin endpoint receives 403 | integration | `pytest backend/tests/test_rbac.py -k test_admin_forbidden` | ❌ W0 | ⬜ pending |
| 01-02-02 | 02 | 2 | AUTH-04 | T-01-04 | 5 consecutive failed logins trigger 15-minute lockout | integration | `pytest backend/tests/test_auth.py -k test_lockout` | ❌ W0 | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

- [ ] `backend/tests/conftest.py` — Test database fixture & client setup
- [ ] `backend/tests/test_auth.py` — Auth unit and integration tests (signup, login, JWT validation, lockout)
- [ ] `backend/tests/test_rbac.py` — RBAC permission checks for User vs Admin roles

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| *All phase behaviors have automated verification.* | | | |

---

## Validation Sign-Off

- [ ] All tasks have `<automated>` verify or Wave 0 dependencies
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify
- [ ] Wave 0 covers all MISSING references
- [ ] No watch-mode flags
- [ ] Feedback latency < 10s
- [ ] `nyquist_compliant: true` set in frontmatter

**Approval:** pending
