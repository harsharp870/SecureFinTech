# Phase 5: User & Admin Frontend Dashboards Context

**Gathered:** 2026-08-13
**Status:** Complete

## Domain Boundary
Phase 5 delivers a modern, responsive, dark-mode web application built with React 18 (Vite + TypeScript) and a custom FinTech cybersecurity design system. It includes Auth screens (Login & Signup), a User Portal (Wallet summary, Send Money form, Transaction History, and Activity Log), an Executive Admin Security Console (KPI metrics grid, Live Transaction Review Queue, Audit Log Explorer, High-Risk User Detector), and an Explainable AI (XAI) Risk Breakdown Modal.

## Key Decisions

### 1. Frontend Architecture & Design System (DASH-04)
- **Framework & Tooling:** React 18 + TypeScript created with Vite in `frontend/`.
- **Icons:** `lucide-react` for crisp security, wallet, and risk icons.
- **Design System:** Custom CSS design system in `frontend/src/index.css`:
  - Dark Slate background (`#0b0f19` / `#111827`)
  - Glassmorphic card containers (`rgba(17, 24, 39, 0.7)` with `backdrop-filter: blur(12px)`)
  - Neon Accent Colors: Cyan `#00f2fe`, Blue `#3b82f6`, Green `#10b981`, Orange `#f59e0b`, Red `#ef4444`
  - Typography: Modern sans-serif (Inter / Outfit)
  - Micro-animations for hover effects, state changes, and modal popups.
- **Authentication Context:** `AuthContext` managing JWT tokens (`access_token`, `refresh_token`), user profile, and automatic role-based routing (redirecting User to `/dashboard` and Admin to `/admin`).

### 2. User Portal Features (DASH-01)
- **Wallet Overview Card:** Auto-provisioned $10,000 balance display, account details, simulated deposit button/modal.
- **Send Money Form:** Transfer form with recipient email/id inputs, amount input with live balance check, optional note, and instant risk feedback notification.
- **Transaction History:** Paginated table with status badges (`APPROVED`, `FLAGGED`, `BLOCKED`), direction filter (`All`, `Sent`, `Received`), status filter, and row click handler opening transaction details.
- **Personal Activity Log:** Personal security and login history list.

### 3. Executive Admin Security Console (DASH-02)
- **RBAC Guard:** Route `/admin` guarded to `ADMIN` role users.
- **Top Security KPI Grid:**
  - Total Volume & Transaction Count
  - Blocked Fraud Count & Block Rate (%)
  - Pending Flagged Review Queue Count
  - Security Events & Threat Intel Alerts Count
- **Console Views:**
  - **Live Transactions & Review Queue:** View all user transactions; click any row to open the XAI Explanation Modal.
  - **Audit Logs Explorer:** Searchable audit trail with filters for Category (`SECURITY_EVENT`, `ADMIN_ACTION`), Severity (`INFO`, `WARNING`, `CRITICAL`), Action, and Actor ID.
  - **High-Risk User Detector:** List of user accounts flagged for elevated risk or blocked transfers.

### 4. Explainable AI (XAI) Visualization Modal (DASH-03)
- Modal opens when clicking any transaction in User or Admin views.
- **Header:** Transaction ID, Reference ID, Timestamp, Amount, Status Badge.
- **Risk Score Gauge:** Circular or bar meter showing score (`0.0` to `100.0`) and Risk Level badge (`LOW`, `MEDIUM`, `HIGH`, `CRITICAL`).
- **Scoring Split Bar:** Visual 60/40 weighted breakdown showing Rules Engine Score vs Scikit-Learn Anomaly Score.
- **Risk Factor Attribution Cards:** Cards detailing triggered rules and ML anomalies (Rule name, Severity, Impact points, Human-readable explanation).
- **Enforcement Action Badge:** Recommended action (`APPROVE`, `FLAG`, `BLOCK`).

## Code Context & Integration Points
- **Frontend Directory:** `frontend/`
- **Package Config:** `frontend/package.json` with React, Vite, Lucide React, Axios / fetch wrapper.
- **API Services:** `frontend/src/services/api.ts` connecting to FastAPI endpoints (`/api/v1/auth/*`, `/api/v1/wallet/*`, `/api/v1/payments/*`, `/api/v1/admin/*`).

## Deferred Ideas
None.
