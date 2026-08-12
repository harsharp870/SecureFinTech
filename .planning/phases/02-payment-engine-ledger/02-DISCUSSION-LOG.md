# Phase 2 Discussion Log: Payment Engine & Ledger

**Date:** 2026-08-13
**Phase:** 02 - Payment Engine & Ledger

## Areas Discussed

### 1. Initial Wallet Funding Strategy
- **Options Presented:**
  1. Auto-fund new users with $10,000 USD simulation balance + provide `POST /api/v1/wallet/deposit` endpoint for testing (Recommended)
  2. Auto-fund only (fixed $10,000 USD default balance on registration, no deposit API)
  3. Zero initial balance on registration, require explicit deposit/faucet API call
- **Selection:** Option 1 (Auto-fund $10,000 + deposit testing API)

### 2. Atomic Transfers & Concurrency Locking Strategy
- **Options Presented:**
  1. DB transaction with row-level pessimistic locking (`SELECT FOR UPDATE`) + double-entry ledger records (Recommended)
  2. Pessimistic locking on wallet balances only
  3. Optimistic locking with version numbers and transfer retries
- **Selection:** Option 1 (Pessimistic row locking + double-entry ledger records)

### 3. Transaction Status Lifecycle & Fraud Evaluator Hooks
- **Options Presented:**
  1. Synchronous evaluator hook: Create pending transaction -> call extensible `FraudEvaluator` hook (mock auto-pass in Phase 2) -> update balance & status (Recommended)
  2. Direct immediate settlement: Auto-approve all transfers in Phase 2
  3. Two-phase reservation: Place sender funds on HOLD, trigger evaluation, then finalize
- **Selection:** Option 1 (Synchronous FraudEvaluator hook interface with mock auto-pass in Phase 2)

### 4. Transaction History & Filtering API
- **Options Presented:**
  1. Limit/offset pagination with filtering by direction, status, date range, search + detail endpoint (Recommended)
  2. Simple transaction history list endpoint
- **Selection:** Option 1 (Paginated history endpoint with direction, status, date range filters + detail view)
