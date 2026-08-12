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

class AIFraudEvaluator(BaseFraudEvaluator):
    """
    Phase 3 AI & Rule-Based Fraud Evaluator.
    Evaluates transaction via feature extractor, deterministic rules engine, and ML IsolationForest.
    """
    def __init__(self, aggregator: HybridFraudAggregator = None):
        self.aggregator = aggregator or HybridFraudAggregator()

    def evaluate(self, db: Session, transaction: Transaction) -> FraudEvaluationResult:
        # Get sender wallet balance for ratio calculation
        sender_wallet = db.query(Wallet).filter(Wallet.user_id == transaction.sender_id).first()
        sender_balance = sender_wallet.balance if sender_wallet else transaction.amount

        # Extract features
        features = extract_feature_vector(
            db=db,
            sender_id=transaction.sender_id,
            amount=transaction.amount,
            sender_wallet_balance=sender_balance
        )

        # Run hybrid evaluation
        xai_result = self.aggregator.evaluate_transaction(features)

        # Serialize risk factors to JSON
        risk_factors_json = json.dumps([rf for rf in xai_result.risk_factors])

        reasons = [rf["description"] for rf in xai_result.risk_factors]

        return FraudEvaluationResult(
            decision=xai_result.action,
            risk_score=xai_result.final_risk_score,
            risk_level=xai_result.risk_level,
            risk_factors=risk_factors_json,
            reasons=reasons
        )

# Active global evaluator for application
default_fraud_evaluator: BaseFraudEvaluator = AIFraudEvaluator()
