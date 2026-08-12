from abc import ABC, abstractmethod
from typing import List, Optional
from pydantic import BaseModel
from sqlalchemy.orm import Session
from app.models.payment import Transaction

class FraudEvaluationResult(BaseModel):
    decision: str  # "APPROVE", "FLAG", "BLOCK"
    risk_score: float = 0.0
    risk_level: str = "LOW"
    reasons: List[str] = []

class BaseFraudEvaluator(ABC):
    @abstractmethod
    def evaluate(self, db: Session, transaction: Transaction) -> FraudEvaluationResult:
        """Evaluates a pending transaction and returns risk score and decision."""
        pass

class Phase2PassThroughEvaluator(BaseFraudEvaluator):
    """
    Phase 2 default evaluator: Mock auto-approves all valid transactions with 0.0 risk score.
    Will be seamlessly replaced in Phase 3 by the real ML & Rule-Based Fraud Detection Engine.
    """
    def evaluate(self, db: Session, transaction: Transaction) -> FraudEvaluationResult:
        return FraudEvaluationResult(
            decision="APPROVE",
            risk_score=0.0,
            risk_level="LOW",
            reasons=["Phase 2 mock pass-through approval"]
        )

# Global default instance for Phase 2
default_fraud_evaluator: BaseFraudEvaluator = Phase2PassThroughEvaluator()
