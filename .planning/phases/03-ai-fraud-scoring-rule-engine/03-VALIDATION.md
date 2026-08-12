# Phase 3: AI Fraud Scoring & Rule Engine Validation Strategy

**Date:** 2026-08-13
**Phase:** 03 - AI Fraud Scoring & Rule Engine

## Dimension 8: Nyquist Validation Framework Compliance

### Test Infrastructure & Execution
- **Framework:** `pytest` + `scikit-learn` / `joblib`
- **Model Storage:** In-memory or temporary `.joblib` model artifact for testing.

### Automated Test Coverage Requirements

1. **Deterministic Rules Engine (`FRAD-03`)**
   - Verify `HighAmountRule` triggers for amounts >= $5k (+40 pts) and >= $10k (hard override).
   - Verify `HighVelocityRule` triggers when > 3 transactions occur in 5 minutes.
   - Verify `RapidSuccessionRule` triggers when transaction occurs < 30s after previous tx.
   - Verify `AccountDrainRule` triggers when amount > 90% of wallet balance.

2. **ML Anomaly Detection Model (`FRAD-04`)**
   - Verify synthetic dataset generator produces 2,000 valid samples and trains `IsolationForest`.
   - Verify ML scoring returns valid 0-100 normalized risk score for normal vs anomalous vectors.

3. **Hybrid Risk Aggregator & XAI Attributions (`FRAD-01`, `FRAD-02`, `FRAD-05`, `FRAD-06`)**
   - Verify 60/40 weighted blend produces exact expected risk score.
   - Verify critical rule override forces score to >= 85 and status to `BLOCK`.
   - Verify 4-tier decision mapping (`LOW`/`MEDIUM`/`HIGH`/`CRITICAL` -> `APPROVE`/`FLAG`/`BLOCK`).
   - Verify XAI structured `risk_factors` JSON output contains human-readable factor descriptions.

4. **End-to-End Payment Integration (`FRAD-06`)**
   - Verify transferring $500 results in `APPROVED` status with low risk score.
   - Verify transferring $12,000 results in `BLOCKED` status with `CRITICAL` risk score and unchanged balances.
   - Verify `GET /api/v1/payments/{id}/xai` returns complete XAI explanation metadata.
