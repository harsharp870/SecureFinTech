import json
from typing import List, Tuple
from pydantic import BaseModel
from app.services.fraud_engine.feature_extractor import TransactionFeatureVector
from app.services.fraud_engine.rules_engine import RulesEngine, RuleResult
from app.services.fraud_engine.ml_detector import MLAnomalyDetector

class XAIExplanation(BaseModel):
    final_risk_score: float
    risk_level: str  # "LOW", "MEDIUM", "HIGH", "CRITICAL"
    action: str      # "APPROVE", "FLAG", "BLOCK"
    rules_score: float
    ml_score: float
    risk_factors: List[dict]

class HybridFraudAggregator:
    def __init__(self, rules_engine: RulesEngine = None, ml_detector: MLAnomalyDetector = None):
        self.rules_engine = rules_engine or RulesEngine()
        self.ml_detector = ml_detector or MLAnomalyDetector()

    def evaluate_transaction(self, features: TransactionFeatureVector) -> XAIExplanation:
        # 1. Deterministic Security Rules Evaluation
        rules_score, triggered_rules, has_critical_override = self.rules_engine.evaluate(features)

        # 2. ML Anomaly Score Evaluation
        ml_score = self.ml_detector.predict_risk_score(features)

        # 3. Hybrid 60/40 Weighted Blend
        final_score = (0.60 * rules_score) + (0.40 * ml_score)

        # 4. Critical Hard Security Rule Override
        if has_critical_override:
            final_score = max(85.0, final_score)

        final_score = float(max(0.0, min(100.0, round(final_score, 2))))

        # 5. Risk Level & Decision Policy Mapping
        if final_score >= 85.0:
            risk_level = "CRITICAL"
            action = "BLOCK"
        elif final_score >= 60.0:
            risk_level = "HIGH"
            action = "FLAG"
        elif final_score >= 30.0:
            risk_level = "MEDIUM"
            action = "APPROVE"
        else:
            risk_level = "LOW"
            action = "APPROVE"

        # 6. Build Structured XAI Risk Factors List
        risk_factors: List[dict] = []
        for r in triggered_rules:
            risk_factors.append({
                "factor_type": "RULE",
                "rule_name": r.rule_name,
                "impact": r.impact,
                "is_critical": r.is_critical_override,
                "description": r.description
            })

        if ml_score >= 50.0:
            risk_factors.append({
                "factor_type": "ML_ANOMALY",
                "rule_name": "ISOLATION_FOREST_ANOMALY",
                "impact": ml_score,
                "is_critical": False,
                "description": f"Statistical anomaly detected by ML IsolationForest model (Anomaly Score: {ml_score}/100)"
            })

        return XAIExplanation(
            final_risk_score=final_score,
            risk_level=risk_level,
            action=action,
            rules_score=rules_score,
            ml_score=ml_score,
            risk_factors=risk_factors
        )
