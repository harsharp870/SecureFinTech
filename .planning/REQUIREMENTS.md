# Requirements: SecureFinTech

**Defined:** 2026-08-13
**Core Value:** Real-time explainable fraud detection coupled with robust cybersecurity controls to detect, score, and prevent fraudulent digital payment transactions.

## v1 Requirements

### Authentication & Security Basics

- [ ] **AUTH-01**: User registration with email, password hashing (Argon2/bcrypt), and role assignment (User/Admin).
- [ ] **AUTH-02**: User authentication via JWT access & refresh tokens with secure session handling.
- [ ] **AUTH-03**: Role-Based Access Control (RBAC) enforcing endpoint access for User vs Admin roles.
- [ ] **AUTH-04**: Account lockout and rate limiting after consecutive failed login attempts.
- [ ] **AUTH-05**: MFA/OTP-ready data models and verification framework.

### Digital Payment & Transaction Engine

- [ ] **PAYM-01**: Simulated digital wallet balance with initial funding and atomic balance transfers.
- [ ] **PAYM-02**: Peer-to-peer transfer API between accounts with transactional consistency.
- [ ] **PAYM-03**: Transaction status lifecycle management (pending, approved, flagged, blocked) with unique IDs and ISO timestamps.
- [ ] **PAYM-04**: Transaction history API with filtering and detail views.

### AI-Powered Fraud Detection Engine

- [ ] **FRAD-01**: Real-time risk scoring engine generating score from 0 to 100 per transaction.
- [ ] **FRAD-02**: Risk level classification: LOW (0-29), MEDIUM (30-59), HIGH (60-84), CRITICAL (85-100).
- [ ] **FRAD-03**: Deterministic security rules engine (amount threshold, frequency, rapid succession, IP/device anomaly).
- [ ] **FRAD-04**: Machine learning anomaly detection model (Scikit-Learn IsolationForest / RandomForest) analyzing feature vectors.
- [ ] **FRAD-05**: Explainable AI (XAI) feature attribution breakdown giving exact human-readable reasons for risk score.
- [ ] **FRAD-06**: Automated action recommendation (APPROVE, FLAG_FOR_REVIEW, BLOCK) based on configurable policies.

### Cybersecurity Monitoring & Audit Logs

- [ ] **SECU-01**: Security event logging for suspicious logins, failed auth, IP changes, and policy violations.
- [ ] **SECU-02**: Global API rate limiting & OWASP security headers (CORS, HSTS, X-Content-Type-Options, input sanitization).
- [ ] **SECU-03**: Simulated threat intelligence provider integration (suspicious IP & device fingerprint lookup).
- [ ] **SECU-04**: Immutable audit log recording all administrative actions and security events.

### Admin & User Dashboards (Frontend)

- [ ] **DASH-01**: User Dashboard: Wallet balance, send money form, transaction history, and personal security alerts.
- [ ] **DASH-02**: Admin Security Console: Real-time fraud statistics, transaction review queue, high-risk user detection, audit trail.
- [ ] **DASH-03**: Fraud Explanation Modal: Visual representation of risk score factors and ML feature attributions.
- [ ] **DASH-04**: Modern dark-mode FinTech / Cybersecurity design system with responsive layouts.

### Testing, Infrastructure & Documentation

- [ ] **INFR-01**: Pytest suite covering backend auth, payments, fraud engine, and security endpoints.
- [ ] **INFR-02**: Frontend component and integration testing suite.
- [ ] **INFR-03**: Dockerfile and Docker Compose orchestration for local PostgreSQL, FastAPI, and React development.
- [ ] **INFR-04**: Comprehensive project documentation (README, Architecture, Threat Model, API docs, Demo instructions).

## Out of Scope

| Feature | Reason |
|---------|--------|
| Real Payment Gateways / Banking APIs | Safe academic simulation environment only |
| Real Money Processing | Educational / Prototype scope |
| Real Credit Card Processing (PCI-DSS Live Network) | Out of academic scope |

## Traceability

| Requirement | Phase | Status |
|-------------|-------|--------|
| AUTH-01 | Phase 1 | Pending |
| AUTH-02 | Phase 1 | Pending |
| AUTH-03 | Phase 1 | Pending |
| AUTH-04 | Phase 1 | Pending |
| AUTH-05 | Phase 1 | Pending |
| PAYM-01 | Phase 2 | Pending |
| PAYM-02 | Phase 2 | Pending |
| PAYM-03 | Phase 2 | Pending |
| PAYM-04 | Phase 2 | Pending |
| FRAD-01 | Phase 3 | Pending |
| FRAD-02 | Phase 3 | Pending |
| FRAD-03 | Phase 3 | Pending |
| FRAD-04 | Phase 3 | Pending |
| FRAD-05 | Phase 3 | Pending |
| FRAD-06 | Phase 3 | Pending |
| SECU-01 | Phase 4 | Pending |
| SECU-02 | Phase 4 | Pending |
| SECU-03 | Phase 4 | Pending |
| SECU-04 | Phase 4 | Pending |
| DASH-01 | Phase 5 | Pending |
| DASH-02 | Phase 5 | Pending |
| DASH-03 | Phase 5 | Pending |
| DASH-04 | Phase 5 | Pending |
| INFR-01 | Phase 6 | Pending |
| INFR-02 | Phase 6 | Pending |
| INFR-03 | Phase 6 | Pending |
| INFR-04 | Phase 6 | Pending |

**Coverage:**
- v1 requirements: 27 total
- Mapped to phases: 27
- Unmapped: 0 ✓

---
*Requirements defined: 2026-08-13*
*Last updated: 2026-08-13 after initial definition*
