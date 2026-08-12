# Phase 3: AI Fraud Scoring & Rule Engine Context

**Gathered:** 2026-08-13
**Status:** Complete

## Domain Boundary
Phase 3 delivers a real-time hybrid fraud detection engine that evaluates every P2P transfer. It combines deterministic security rules (amount thresholds, velocity, rapid succession, balance drain) with a Scikit-Learn `IsolationForest` machine learning anomaly detection model, producing a 0–100 risk score, 4-tier risk classification, Explainable AI (XAI) feature attributions, and automated action enforcement (`APPROVE`, `FLAG`, `BLOCK`).

## Key Decisions

### Hybrid Risk Aggregation Strategy
- **Weighted Score Composition:** 60% Deterministic Rules Score + 40% ML Model Anomaly Score.
- **Hard Security Rule Override:** If a CRITICAL rule trips (e.g. transfer >= $10,000.00 or blacklisted entity), the risk score is immediately forced to 85+ (`CRITICAL` / `BLOCK`), overriding low ML scores.
- **Risk Score Range:** Normalized from `0.0` (zero risk) to `100.0` (maximum risk).

### Deterministic Security Rules & Thresholds
1. **High Amount Rule:**
   - Amount >= $5,000.00: +40 risk points (`HIGH` alert).
   - Amount >= $10,000.00: +85 risk points (Triggers hard `CRITICAL` / `BLOCK` override).
2. **High Velocity Rule:**
   - > 3 transfers within a 5-minute sliding window: +35 risk points.
3. **Rapid Succession Rule:**
   - Transfer initiated < 30 seconds after previous transaction by same user: +30 risk points.
4. **Account Drain Rule:**
   - Transfer amount > 90% of available wallet balance: +25 risk points.

### ML Anomaly Detection Model & Training Setup
- **Algorithm:** Scikit-Learn `IsolationForest` (`contamination=0.05`, `n_estimators=100`, `random_state=42`).
- **Feature Vector:** `[amount, velocity_5m, seconds_since_last_tx, balance_ratio, hour_of_day]`.
- **Synthetic Baseline Generator:** On application startup, if `backend/app/ml/models/isolation_forest.joblib` does not exist, auto-generate 2,000 synthetic transaction feature vectors (95% normal consumer activity, 5% anomalous spikes), train the model, and persist `.joblib` to disk for fast inference (< 5ms per check).

### Explainable AI (XAI) & Action Policy
- **Risk Tiers & Actions:**
  - `0 - 29` (**LOW**): `APPROVE` transaction, settle balances immediately.
  - `30 - 59` (**MEDIUM**): `APPROVE` transaction with warning log.
  - `60 - 84` (**HIGH**): `FLAG` transaction for admin review queue (hold balance).
  - `85 - 100` (**CRITICAL**): `BLOCK` transaction instantly, reject balance transfer.
- **Structured XAI Output:** Store `risk_factors` as JSON string / JSON column on `Transaction` model:
  ```json
  [
    {"rule": "HIGH_AMOUNT", "impact": 40, "description": "Transfer amount ($6,500.00) exceeds $5,000 threshold"},
    {"rule": "HIGH_VELOCITY", "impact": 35, "description": "4 transfers executed within 5 minutes"}
  ]
  ```

## Code Context & Integration Points
- **Existing Hook:** `FraudEvaluator` interface in `backend/app/services/fraud_evaluator.py`.
- **Existing Payment Service:** `execute_p2p_transfer` in `backend/app/services/payment.py`.
- **New Engine Package:** `backend/app/services/fraud_engine/`
  - `rules_engine.py` (Deterministic security rules).
  - `ml_detector.py` (Scikit-Learn IsolationForest model loader/trainer).
  - `hybrid_aggregator.py` (Weighted scoring, override logic, XAI generator).
- **New API Endpoint:** `GET /api/v1/payments/{id}/xai` (Detailed risk score explanation for user/admin dashboards).

## Deferred Ideas
None.
