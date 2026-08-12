# Phase 2: Payment Engine & Ledger Context

**Gathered:** 2026-08-13
**Status:** Complete

## Domain Boundary
Phase 2 delivers atomic digital wallet balance simulation, peer-to-peer (P2P) transfers with strict transactional consistency, status lifecycle management (`pending`, `approved`, `flagged`, `blocked`), and transaction history APIs with filtering and detail lookups.

## Key Decisions

### Wallet Model & Funding Strategy
- **Auto-funding on Registration:** New users are automatically initialized with a simulated balance of $10,000.00 USD upon account creation (`AUTH-01` hook / `Wallet` initialization).
- **Deposit API for Testing:** Expose `POST /api/v1/wallet/deposit` allowing users/admins to add simulation funds for test scenarios.
- **Single Currency:** USD simulation credits (`USD`) used across all balance operations in v1.

### Atomic Transfers & Locking Strategy
- **Row-Level Pessimistic Locking:** P2P transfers execute inside a single DB transaction utilizing `SELECT ... FOR UPDATE` on wallet rows (sorted by ID to prevent deadlocks).
- **Double-Entry Ledger Architecture:** Every transfer writes immutable transaction entries with sender debit and recipient credit logs, maintaining auditability and balance safety.
- **Validation:** Transfers enforce non-negative balances, sender ownership, self-transfer prevention, and active account state before balance mutation.

### Transaction Lifecycle & Fraud Evaluator Hook
- **Status Lifecycle:** `PENDING` -> `APPROVED` | `FLAGGED` | `BLOCKED`.
- **Synchronous Fraud Evaluator Interface:** Transfers create a `PENDING` transaction record and trigger a modular `FraudEvaluator` hook interface.
- **Phase 2 Pass-Through:** In Phase 2, `FraudEvaluator` returns a mock `APPROVE` decision. In Phase 3, this hook will be replaced seamlessly by the ML & Rule-Based Fraud Detection Engine (`FRAD-01` to `FRAD-06`).
- **State Enforcement:** Wallet balances are debited/credited ONLY when the transaction evaluation result is `APPROVED`.

### Transaction History & Detail API
- **Paginated History Endpoint:** `GET /api/v1/payments/history` with `page` and `size` parameters.
- **Filtering Parameters:** Filter history by direction (`sent`, `received`, `all`), status (`approved`, `flagged`, `blocked`, `pending`), date range (`start_date`, `end_date`), and counterparty.
- **Detail Lookup:** `GET /api/v1/payments/{transaction_id}` returning full transaction fields including timestamps, status, sender/recipient details, and risk evaluation metadata.

## Code Context & Integration Points
- **Existing Models:** `backend/app/models/user.py`
- **Existing Auth:** `backend/app/api/deps.py` (`get_current_user`)
- **New Models:** `Wallet`, `Transaction` (`backend/app/models/payment.py`)
- **New Schemas:** `backend/app/schemas/payment.py`
- **New Services:** `backend/app/services/payment.py` (atomic transfer logic, row-locking)
- **New API Router:** `backend/app/api/v1/payments.py` & `backend/app/api/v1/wallet.py`

## Deferred Ideas
None.
