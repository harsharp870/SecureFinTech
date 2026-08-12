# Roadmap: SecureFinTech

## Overview

SecureFinTech is built in six distinct phases. We begin with foundation & authentication, build the payment engine ledger, create the AI fraud scoring & XAI rules engine, implement cybersecurity event logging & API security controls, build the dark-mode React frontend dashboards (User & Admin), and finalize with comprehensive automated testing, Docker containerization, and security documentation.

## Phases

- [ ] **Phase 1: Foundation & Authentication** - PostgreSQL schema, FastAPI backend setup, JWT auth, RBAC (User/Admin), password hashing, rate limiting, and lockout.
- [ ] **Phase 2: Payment Engine & Ledger** - Wallet balance management, atomic P2P transfers, transaction status lifecycle, and transaction history.
- [ ] **Phase 3: AI Fraud Scoring & Rule Engine** - Hybrid fraud engine (deterministic security rules + Scikit-Learn anomaly detector), XAI feature attribution, and automated risk actions.
- [ ] **Phase 4: Cybersecurity & Audit Logging** - Security event logger, OWASP API controls, threat intelligence simulation, and immutable audit logs.
- [ ] **Phase 5: User & Admin Frontend Dashboards** - React (Vite + TS) dark-mode UI, User transaction portal, Admin security console with XAI visualizations.
- [ ] **Phase 6: Testing, Docker & Documentation** - Pytest suite, Docker Compose setup, Threat Model, API docs, and demo guides.

## Phase Details

### Phase 1: Foundation & Authentication
**Goal**: Secure, robust backend foundation with user registration, authentication, RBAC, and rate limiting.
**Depends on**: Nothing
**Requirements**: AUTH-01, AUTH-02, AUTH-03, AUTH-04, AUTH-05
**Success Criteria**:
  1. User can register with email/password and login to receive JWT tokens.
  2. RBAC middleware restricts admin endpoints to Admin users only.
  3. Failed login attempts trigger rate limiting and account lockout after 5 consecutive failures.
**Plans**: 2 plans

Plans:
- [ ] 01-01: Setup FastAPI project structure, PostgreSQL database connection, SQLAlchemy ORM models, and Alembic migrations.
- [ ] 01-02: Implement Auth router (signup, login, JWT issuance, password hashing), RBAC middleware, and login rate limiter / account lockout.

### Phase 2: Payment Engine & Ledger
**Goal**: Atomic, secure digital payment simulation and transaction history.
**Depends on**: Phase 1
**Requirements**: PAYM-01, PAYM-02, PAYM-03, PAYM-04
**Success Criteria**:
  1. Users have simulated wallet balances that update atomically upon P2P transfer.
  2. Transactions transition through status lifecycle (pending, approved, flagged, blocked).
  3. Users can view their transaction history with timestamps and status details.
**Plans**: 2 plans

Plans:
- [ ] 02-01: Create Wallet and Transaction database schemas, balance update logic with database transactions.
- [ ] 02-02: Implement Payment API endpoints (transfer, transaction history, detail lookup) and validation logic.

### Phase 3: AI Fraud Scoring & Rule Engine
**Goal**: Real-time hybrid fraud detection engine with explainable AI (XAI) risk scoring.
**Depends on**: Phase 2
**Requirements**: FRAD-01, FRAD-02, FRAD-03, FRAD-04, FRAD-05, FRAD-06
**Success Criteria**:
  1. Engine calculates real-time risk score (0-100) and risk level (LOW/MEDIUM/HIGH/CRITICAL) for every transfer.
  2. Hybrid engine evaluates deterministic security rules and Scikit-Learn anomaly model.
  3. Engine returns human-readable feature attribution explanations for risk scores.
  4. System automatically approves, flags, or blocks transactions based on risk score thresholds.
**Plans**: 2 plans

Plans:
- [ ] 03-01: Build deterministic security rules engine (amount thresholds, velocity, IP/device anomaly) and feature extractor.
- [ ] 03-02: Build Scikit-Learn anomaly model (IsolationForest), hybrid risk score aggregator, XAI explanation generator, and hook into payment execution.

### Phase 4: Cybersecurity & Audit Logging
**Goal**: Enterprise-grade security event monitoring, OWASP API protection, and audit logging.
**Depends on**: Phase 3
**Requirements**: SECU-01, SECU-02, SECU-03, SECU-04
**Success Criteria**:
  1. Security event logger records all suspicious logins, failed auth, and flagged transactions.
  2. API endpoints are protected by global rate limiting, input sanitization, and OWASP security headers.
  3. Threat intelligence service flags known malicious IP addresses and device fingerprints.
**Plans**: 2 plans

Plans:
- [ ] 04-01: Implement SecurityEvent and AuditLog schemas, logger middleware, and OWASP security header middleware.
- [ ] 04-02: Build Threat Intelligence lookup module and integrate security event alerts into transaction processing.

### Phase 5: User & Admin Frontend Dashboards
**Goal**: Modern responsive dark-mode web application for users and security administrators.
**Depends on**: Phase 4
**Requirements**: DASH-01, DASH-02, DASH-03, DASH-04
**Success Criteria**:
  1. User portal enables account management, wallet balance viewing, money transfers, and security alerts.
  2. Admin Security Console visualizes real-time transaction stats, fraud risk metrics, flagged review queue, and audit logs.
  3. Fraud Explanation modal displays visual XAI score breakdown and contributing risk features.
**Plans**: 3 plans

Plans:
- [ ] 05-01: Setup React (Vite + TS) frontend architecture, custom CSS cybersecurity dark-mode design system, and Auth context.
- [ ] 05-02: Build User Portal (wallet summary, send money form, transaction history, activity log).
- [ ] 05-03: Build Admin Security Console (metrics grid, live transaction monitor, XAI fraud breakdown modal, audit log viewer).

### Phase 6: Testing, Docker & Documentation
**Goal**: Production-ready automated test coverage, Docker Compose orchestration, and comprehensive security documentation.
**Depends on**: Phase 5
**Requirements**: INFR-01, INFR-02, INFR-03, INFR-04
**Success Criteria**:
  1. Pytest suite validates all backend auth, payment, fraud scoring, and security API endpoints.
  2. Docker Compose brings up PostgreSQL, FastAPI backend, and React frontend with a single command.
  3. Documentation includes README, Threat Model, API Architecture, Database Schema, and Demo Guide.
**Plans**: 2 plans

Plans:
- [ ] 06-01: Implement Pytest test suite for backend APIs, fraud engine, and security controls + frontend component tests.
- [ ] 06-02: Build Dockerfile, docker-compose.yml, environment templates, README.md, Threat Model, and API documentation.

## Progress

**Execution Order:**
Phases execute in numeric order: 1 → 2 → 3 → 4 → 5 → 6

| Phase | Plans Complete | Status | Completed |
|-------|----------------|--------|-----------|
| 1. Foundation & Authentication | 0/2 | Not started | - |
| 2. Payment Engine & Ledger | 0/2 | Not started | - |
| 3. AI Fraud Scoring & Rule Engine | 0/2 | Not started | - |
| 4. Cybersecurity & Audit Logging | 0/2 | Not started | - |
| 5. User & Admin Frontend Dashboards | 0/3 | Not started | - |
| 6. Testing, Docker & Documentation | 0/2 | Not started | - |
