# Phase 3 Discussion Log: AI Fraud Scoring & Rule Engine

**Date:** 2026-08-13
**Phase:** 03 - AI Fraud Scoring & Rule Engine

## Areas Discussed

### 1. Hybrid Risk Aggregation Strategy
- **Options Presented:**
  1. Hybrid weighted blend (60% Rules / 40% ML) with CRITICAL rule override (Recommended)
  2. Max-score strategy: Final Risk Score = max(Rules Score, ML Anomaly Score)
  3. Equal 50/50 weighted blend without rule overrides
- **Selection:** Option 1 (60% Rules / 40% ML blend + CRITICAL hard rule override)

### 2. Deterministic Security Rules & Thresholds
- **Options Presented:**
  1. Comprehensive rule set: High Amount (>= $5k / >= $10k), Velocity (>3 in 5m), Rapid Succession (<30s), Account Drain (>90% balance) (Recommended)
  2. Basic rule set: High Amount (>= $5k) and Hourly Velocity (>5 in 1h) only
- **Selection:** Option 1 (Comprehensive rule set: High Amount, Velocity, Rapid Succession, Account Drain)

### 3. ML Anomaly Model Training Setup
- **Options Presented:**
  1. Synthetic baseline dataset generator (trains IsolationForest on app startup if model file missing, persists to .joblib) (Recommended)
  2. Pre-generated static .joblib model file stored in repository
- **Selection:** Option 1 (Synthetic dataset generator on startup + joblib persistence)

### 4. Explainable AI (XAI) Structure & Decision Policy
- **Options Presented:**
  1. Structured JSON risk_factors array on Transaction + 4-tier decision policy (0-29 LOW/APPROVE, 30-59 MEDIUM/APPROVE, 60-84 HIGH/FLAG, 85-100 CRITICAL/BLOCK) (Recommended)
  2. Basic summary text string on Transaction with 3-tier policy
- **Selection:** Option 1 (Structured JSON risk_factors array + 4-tier policy)
