# SecureFinTech

## What This Is

SecureFinTech is a production-quality academic cybersecurity and FinTech prototype simulating a digital payment ecosystem integrated with a real-time AI-powered fraud detection scoring engine and comprehensive security monitoring dashboard.

## Core Value

Real-time explainable fraud detection coupled with robust cybersecurity controls to detect, score, and prevent fraudulent digital payment transactions.

## Requirements

### Validated

- ✓ GSD planning framework and codebase map initialized — Phase 0

### Active

- [ ] Secure User Authentication: JWT authentication, RBAC (User/Admin), password hashing (Argon2/bcrypt), MFA/OTP readiness, session handling, rate limiting & lockout
- [ ] Digital Payment Simulation: Wallet balance, peer-to-peer transfers, transaction lifecycle tracking (pending, approved, flagged, blocked), transaction audit trail
- [ ] AI-Powered Fraud Detection Engine: Hybrid explainable rule engine + ML anomaly detection (0–100 risk score, LOW/MEDIUM/HIGH/CRITICAL levels, feature attribution reasons, action recommendation)
- [ ] Cybersecurity Monitoring & Controls: Rate limiting, input validation/sanitization, OWASP API security controls, security event logging, suspicious activity detection, basic threat intelligence integration
- [ ] Admin Security Dashboard: Real-time metrics, transaction monitor, fraud explanations, high-risk user alerts, security event logs
- [ ] User Dashboard: Account overview, transfer interface, transaction history & status, security alerts, login/activity log
- [ ] Modular Backend & Database: FastAPI (Python 3.11+), Pydantic v2, PostgreSQL, SQLAlchemy ORM, database migrations
- [ ] Modern Responsive Frontend: React (Vite + TypeScript), custom CSS dark-mode FinTech/cybersecurity UI design system
- [ ] Testing & Security Validation: Pytest unit & integration tests, fraud engine tests, security API tests, frontend component tests
- [ ] Containerized Deployment: Dockerfile and Docker Compose environment for local orchestrations

### Out of Scope

- Real banking/payment gateway integration — Safe simulated environment only
- Real money transactions — Academic prototype scoping

## Context

- Designed as an academic-grade demonstration of AI-driven cybersecurity in financial applications.
- Built with an emphasis on explainable AI (XAI) feature importance so security analysts understand why a transaction was flagged or blocked.

## Constraints

- **Security**: Must adhere to OWASP Top 10 API Security guidelines (no plaintext secrets, strict validation, centralized error handling).
- **Tech Stack**: Python (FastAPI) backend, Scikit-Learn ML engine, React (Vite + TypeScript) frontend, PostgreSQL database.
- **Environment**: Docker & Docker Compose containerized setup.

## Key Decisions

| Decision | Rationale | Outcome |
|----------|-----------|---------|
| Python (FastAPI + Scikit-Learn) Backend | High-performance async APIs with seamless Python ML library integration | ✓ Good |
| React (Vite + TS) + Custom CSS | Modern, fast build tooling with full control over dark-mode cybersecurity aesthetic | ✓ Good |
| PostgreSQL + Docker Compose | Industry-standard relational DB with easy local container deployment | ✓ Good |
| Explainable Hybrid Fraud Engine | Combines deterministic security rules with ML anomaly scoring for transparent decisions | ✓ Good |

---
*Last updated: 2026-08-13 after initialization*

## Evolution

This document evolves at phase transitions and milestone boundaries.

**After each phase transition** (via `/gsd-transition`):
1. Requirements invalidated? → Move to Out of Scope with reason
2. Requirements validated? → Move to Validated with phase reference
3. New requirements emerged? → Add to Active
4. Decisions to log? → Add to Key Decisions
5. "What This Is" still accurate? → Update if drifted

**After each milestone** (via `/gsd-complete-milestone`):
1. Full review of all sections
2. Core Value check — still the right priority?
3. Audit Out of Scope — reasons still valid?
4. Update Context with current state
