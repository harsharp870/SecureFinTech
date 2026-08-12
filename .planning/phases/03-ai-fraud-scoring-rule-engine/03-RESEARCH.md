# Phase 3: AI Fraud Scoring & Rule Engine Technical Research

**Date:** 2026-08-13
**Phase:** 03 - AI Fraud Scoring & Rule Engine
**Status:** Complete

## Executive Summary
Phase 3 builds the real-time hybrid fraud detection engine for SecureFinTech. It couples deterministic security rules with a machine learning anomaly detection model (`IsolationForest` via `scikit-learn`), generating explainable AI (XAI) feature attributions and enforcing automated risk actions (`APPROVE`, `FLAG`, `BLOCK`).

---

## 1. Machine Learning Anomaly Detection (`scikit-learn`)

### 1.1 Model Selection & Configuration
- **Algorithm:** `sklearn.ensemble.IsolationForest`
- **Hyperparameters:** `n_estimators=100`, `contamination=0.05`, `random_state=42`
- **Feature Vector Schema:**
  1. `amount` (float): Transaction amount in USD.
  2. `velocity_5m` (int): Number of transactions by sender in the last 5 minutes.
  3. `seconds_since_last_tx` (float): Seconds elapsed since previous transaction (default 86400 for first tx).
  4. `balance_ratio` (float): Ratio of transfer amount to available wallet balance (`amount / balance`).
  5. `hour_of_day` (int): Hour of transaction in UTC (0 - 23).

### 1.2 Model Persistence & Initialization
- **Model Storage:** `backend/app/ml/models/isolation_forest.joblib`
- **Synthetic Baseline Generator:** If the `.joblib` file is missing on app startup:
  - Generate 2,000 synthetic transaction feature vectors (1,900 normal consumer patterns, 100 anomalous high-amount/burst patterns using `numpy`).
  - Fit `IsolationForest` on the synthetic dataset.
  - Serialize to `isolation_forest.joblib` via `joblib.dump()`.

### 1.3 Score Normalization
`IsolationForest.score_samples(X)` returns raw anomaly scores (typically between -0.5 and 0.5 where lower indicates higher anomaly).
Normalization formula to 0–100 risk score:
```python
raw_score = model.score_samples([feature_vector])[0]
# Normalization: map raw_score from [-0.5, 0.2] to [100.0, 0.0]
ml_risk_score = max(0.0, min(100.0, (0.2 - raw_score) * 142.85))
```

---

## 2. Deterministic Security Rules Engine

### 2.1 Rule Specifications
```python
class RuleResult(BaseModel):
    rule_name: str
    impact: float
    is_critical_override: bool = False
    description: str
```

1. **High Amount Rule**:
   - `amount >= $10,000.00` $\rightarrow$ Impact: 85.0, Critical Override: True ("High value transaction exceeds $10,000 safety threshold").
   - `amount >= $5,000.00` $\rightarrow$ Impact: 40.0, Critical Override: False ("High value transaction exceeds $5,000 threshold").
2. **High Velocity Rule**:
   - `velocity_5m > 3` $\rightarrow$ Impact: 35.0, Critical Override: False ("High velocity: 4+ transactions in 5 minutes").
3. **Rapid Succession Rule**:
   - `seconds_since_last_tx < 30.0` $\rightarrow$ Impact: 30.0, Critical Override: False ("Rapid succession: transaction executed within 30 seconds of previous transfer").
4. **Account Drain Rule**:
   - `balance_ratio > 0.9` $\rightarrow$ Impact: 25.0, Critical Override: False ("Account drain pattern: transaction consumes over 90% of wallet balance").

---

## 3. Hybrid Risk Score Aggregator & XAI Engine

### 3.1 Aggregation Logic
```python
rules_score = sum(r.impact for r in triggered_rules)
rules_score = min(100.0, rules_score)

# Hybrid blend: 60% Rules + 40% ML
final_score = (0.60 * rules_score) + (0.40 * ml_risk_score)

# Check for hard critical rule override
if any(r.is_critical_override for r in triggered_rules):
    final_score = max(85.0, final_score)

final_score = min(100.0, max(0.0, final_score))
```

### 3.2 Decision Policy & Risk Classification
- `0.0 - 29.9`: Level `LOW`, Decision `APPROVE`
- `30.0 - 59.9`: Level `MEDIUM`, Decision `APPROVE`
- `60.0 - 84.9`: Level `HIGH`, Decision `FLAG`
- `85.0 - 100.0`: Level `CRITICAL`, Decision `BLOCK`

---

## 4. Integration & XAI Endpoint

- **Integration Point:** `AIFraudEvaluator` implements `BaseFraudEvaluator` in `backend/app/services/fraud_evaluator.py`, called during `execute_p2p_transfer`.
- **XAI Endpoint:** `GET /api/v1/payments/{id}/xai` returning detailed feature breakdown, ML anomaly score, triggered rules, and explanation narrative.
