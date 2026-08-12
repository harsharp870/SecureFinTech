import json
from abc import ABC, abstractmethod
from typing import List, Optional
from pydantic import BaseModel
from sqlalchemy.orm import Session
from app.models.payment import Transaction, Wallet
from app.services.fraud_engine.feature_extractor import extract_feature_vector
from app.services.fraud_engine.hybrid_aggregator import HybridFraudAggregator

class FraudEvaluationResult(BaseModel):
    decision: str  # "APPROVE", "FLAG", "BLOCK"
    risk_score: float = 0.0
    risk_level: str = "LOW"
    risk_factors: Optional[str] = None
    reasons: List[str] = []

class BaseFraudEvaluator(ABC):
    @abstractmethod
    def evaluate(self, db: Session, transaction: Transaction) -> FraudEvaluationResult:
        """Evaluates a pending transaction and returns risk score and decision."""
        pass

class Phase2PassThroughEvaluator(BaseFraudEvaluator):
    def evaluate(self, db: Session, transaction: Transaction) -> FraudEvaluationResult:
        return FraudEvaluationResult(
            decision="APPROVE",
            risk_score=0.0,
            risk_level="LOW",
            reasons=["Phase 2 mock pass-through approval"]
        )

from app.services.threat_intel import ThreatIntelService
from app.services.audit_service import log_audit_event
from app.models.audit import AuditCategory, AuditSeverity

class AIFraudEvaluator(BaseFraudEvaluator):
    """
    Phase 3 & 4 AI, Rule-Based & Threat Intel Fraud Evaluator.
    Evaluates transaction via feature extractor, deterministic rules engine, ML IsolationForest, and Threat Intelligence IP lookup.
    """
    def __init__(self, aggregator: HybridFraudAggregator = None, threat_intel: ThreatIntelService = None):
        self.aggregator = aggregator or HybridFraudAggregator()
        self.threat_intel = threat_intel or ThreatIntelService()

    def evaluate(self, db: Session, transaction: Transaction, client_ip: Optional[str] = None) -> FraudEvaluationResult:
        # Get sender wallet balance for ratio calculation
        sender_wallet = db.query(Wallet).filter(Wallet.user_id == transaction.sender_id).first()
        sender_balance = sender_wallet.balance if sender_wallet else transaction.amount

        # 1. Threat Intelligence IP check
        threat_result = self.threat_intel.evaluate_ip(client_ip or "0.0.0.0")

        # 2. Extract features & run hybrid evaluation
        features = extract_feature_vector(
            db=db,
            sender_id=transaction.sender_id,
            amount=transaction.amount,
            sender_wallet_balance=sender_balance
        )
        xai_result = self.aggregator.evaluate_transaction(features)

        decision = xai_result.action
        final_risk_score = xai_result.final_risk_score
        risk_level = xai_result.risk_level
        risk_factors = list(xai_result.risk_factors)

        # Apply Threat Intelligence override if threat score >= 80.0
        if threat_result.is_malicious and threat_result.threat_score >= 80.0:
            decision = "BLOCK"
            risk_level = "CRITICAL"
            final_risk_score = max(90.0, final_risk_score)
            risk_factors.append({
                "factor_type": "THREAT_INTEL",
                "rule_name": threat_result.threat_category,
                "impact": threat_result.threat_score,
                "is_critical": True,
                "description": f"Threat Intelligence IP alert: {threat_result.description} (IP: {threat_result.ip_address})"
            })

            # Record CRITICAL Security Event in Audit Log
            log_audit_event(
                db=db,
                action="THREAT_INTEL_BLOCKED_TRANSACTION",
                category=AuditCategory.SECURITY_EVENT.value,
                severity=AuditSeverity.CRITICAL.value,
                actor_id=transaction.sender_id,
                ip_address=client_ip,
                details={
                    "transaction_id": transaction.id,
                    "amount": float(transaction.amount),
                    "threat_category": threat_result.threat_category,
                    "threat_score": threat_result.threat_score
                }
            )

        # Log security audit events for FLAGGED or BLOCKED transactions
        if decision in ["FLAG", "BLOCK"] and not (threat_result.is_malicious and threat_result.threat_score >= 80.0):
            log_audit_event(
                db=db,
                action=f"P2P_TRANSFER_{decision}ED",
                category=AuditCategory.SECURITY_EVENT.value,
                severity=AuditSeverity.WARNING.value if decision == "FLAG" else AuditSeverity.CRITICAL.value,
                actor_id=transaction.sender_id,
                ip_address=client_ip,
                details={
                    "transaction_id": transaction.id,
                    "amount": float(transaction.amount),
                    "risk_score": final_risk_score,
                    "risk_level": risk_level
                }
            )

        # Serialize risk factors to JSON
        risk_factors_json = json.dumps(risk_factors)
        reasons = [rf["description"] for rf in risk_factors]

        return FraudEvaluationResult(
            decision=decision,
            risk_score=final_risk_score,
            risk_level=risk_level,
            risk_factors=risk_factors_json,
            reasons=reasons
        )


# Active global evaluator for application
default_fraud_evaluator: BaseFraudEvaluator = AIFraudEvaluator()
