# Phase 4: Cybersecurity & Audit Logging Context

**Gathered:** 2026-08-13
**Status:** Complete

## Domain Boundary
Phase 4 delivers enterprise-grade cybersecurity monitoring, OWASP API protection middleware, threat intelligence simulation, and immutable database audit logging. It captures security events across authentication and payment operations, enforces security response headers, performs IP reputation lookups, and provides admin endpoints to query security audit trails.

## Key Decisions

### 1. Audit Logging Architecture (SECU-01, SECU-04)
- **Unified DB Model:** `AuditLog` table in PostgreSQL database.
- **Fields:**
  - `id`: UUID Primary Key (`String(36)`)
  - `category`: `SECURITY_EVENT`, `ADMIN_ACTION`, `SYSTEM_ALERT`
  - `severity`: `INFO`, `WARNING`, `CRITICAL`
  - `action`: String (e.g., `LOGIN_SUCCESS`, `LOGIN_FAILED`, `ACCOUNT_LOCKED`, `P2P_TRANSFER_BLOCKED`, `THREAT_INTEL_ALERT`)
  - `actor_id`: Optional FK to `users.id`
  - `ip_address`: Client IP address string
  - `user_agent`: Optional HTTP User-Agent string
  - `details`: JSON payload string storing event-specific details (e.g. threat score, reason, payment reference)
  - `created_at`: UTC timestamp
- **Admin Query API:** `GET /api/v1/admin/audit-logs` endpoint with filter support (by category, severity, action, actor_id, date range) and pagination, restricted to `ADMIN` role.

### 2. OWASP API Security Controls (SECU-02)
- **Security Headers Middleware:** Custom FastAPI middleware (`SecurityHeadersMiddleware` in `backend/app/core/middleware.py`) setting:
  - `X-Frame-Options: DENY`
  - `X-Content-Type-Options: nosniff`
  - `X-XSS-Protection: 1; mode=block`
  - `Strict-Transport-Security: max-age=31536000; includeSubDomains`
  - `Content-Security-Policy: default-src 'self'`
- **Input Sanitization Filter:** Middleware / utility function stripping suspicious HTML / script tags from request payloads.

### 3. Threat Intelligence Simulation Service (SECU-03)
- **Service Class:** `ThreatIntelService` in `backend/app/services/threat_intel.py`.
- **Deterministic Mock Database:** Pre-configured subnet lookup table for malicious IP ranges:
  - `185.220.101.0/24`: Tor Exit Node Network (Threat Score: `90.0`, Category: `TOR_EXIT_NODE`)
  - `198.51.100.0/24`: Botnet Command & Control (Threat Score: `95.0`, Category: `BOTNET_C2`)
  - `203.0.113.0/24`: Malicious Proxy Network (Threat Score: `85.0`, Category: `MALICIOUS_PROXY`)
- **Lookup Method:** `evaluate_ip(ip_address: str) -> ThreatIntelResult` returning threat score, category, and malicious flag.

### 4. Automated Threat Action Enforcement (SECU-01, SECU-03)
- **Fraud Engine Hook:** `AIFraudEvaluator` integrates `ThreatIntelService`.
- **Action Threshold:** If incoming client IP has threat score $\ge 80.0$:
  - Transaction decision is automatically overridden to `BLOCK`.
  - Automatically logs a `CRITICAL` `SECURITY_EVENT` in `AuditLog` table with action `THREAT_INTEL_BLOCKED_TRANSACTION`.
- **Auth Service Hook:** Login endpoint (`POST /api/v1/auth/login`) checks threat intel on failed logins or suspicious IPs, logging a `WARNING` or `CRITICAL` `SECURITY_EVENT`.

## Code Context & Integration Points
- **New Database Model:** `AuditLog` in `backend/app/models/audit.py`.
- **New Audit Service & Logger:** `backend/app/services/audit_service.py` with `log_security_event()` helper.
- **New Threat Intel Module:** `backend/app/services/threat_intel.py`.
- **New Middleware:** `SecurityHeadersMiddleware` in `backend/app/core/middleware.py`.
- **New Admin Router:** `backend/app/api/v1/admin.py` for `/api/v1/admin/audit-logs`.
- **Existing Integrations:**
  - `backend/app/api/v1/auth.py` -> calls `log_security_event` on login events / lockouts.
  - `backend/app/services/fraud_evaluator.py` -> queries `ThreatIntelService` and logs security audit events.

## Deferred Ideas
None.
