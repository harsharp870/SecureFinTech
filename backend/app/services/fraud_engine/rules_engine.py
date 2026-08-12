from abc import ABC, abstractmethod
from typing import List, Tuple, Optional

from pydantic import BaseModel
from app.services.fraud_engine.feature_extractor import TransactionFeatureVector

class RuleResult(BaseModel):
    rule_name: str
    impact: float
    is_critical_override: bool = False
    description: str

class BaseRule(ABC):
    @abstractmethod
    def evaluate(self, features: TransactionFeatureVector) -> Optional[RuleResult]:
        pass

class HighAmountRule(BaseRule):
    def evaluate(self, features: TransactionFeatureVector) -> Optional[RuleResult]:
        if features.amount >= 10000.0:
            return RuleResult(
                rule_name="HIGH_AMOUNT_CRITICAL",
                impact=85.0,
                is_critical_override=True,
                description=f"Critical high-value transfer (${features.amount:,.2f}) exceeds $10,000 safety threshold"
            )
        elif features.amount >= 5000.0:
            return RuleResult(
                rule_name="HIGH_AMOUNT_ELEVATED",
                impact=40.0,
                is_critical_override=False,
                description=f"Elevated transfer amount (${features.amount:,.2f}) exceeds $5,000 threshold"
            )
        return None

class HighVelocityRule(BaseRule):
    def evaluate(self, features: TransactionFeatureVector) -> Optional[RuleResult]:
        if features.velocity_5m > 3:
            return RuleResult(
                rule_name="HIGH_VELOCITY",
                impact=35.0,
                is_critical_override=False,
                description=f"High transaction frequency: {features.velocity_5m} transfers initiated within 5 minutes"
            )
        return None

class RapidSuccessionRule(BaseRule):
    def evaluate(self, features: TransactionFeatureVector) -> Optional[RuleResult]:
        if features.seconds_since_last_tx < 30.0:
            return RuleResult(
                rule_name="RAPID_SUCCESSION",
                impact=30.0,
                is_critical_override=False,
                description=f"Rapid succession: transfer initiated {int(features.seconds_since_last_tx)}s after previous transaction"
            )
        return None

class AccountDrainRule(BaseRule):
    def evaluate(self, features: TransactionFeatureVector) -> Optional[RuleResult]:
        if features.balance_ratio > 0.90:
            return RuleResult(
                rule_name="ACCOUNT_DRAIN",
                impact=25.0,
                is_critical_override=False,
                description=f"Account drain pattern: transfer consumes {int(features.balance_ratio * 100)}% of available wallet balance"
            )
        return None

class RulesEngine:
    def __init__(self):
        self.rules: List[BaseRule] = [
            HighAmountRule(),
            HighVelocityRule(),
            RapidSuccessionRule(),
            AccountDrainRule(),
        ]

    def evaluate(self, features: TransactionFeatureVector) -> Tuple[float, List[RuleResult], bool]:
        triggered_results: List[RuleResult] = []
        total_impact = 0.0
        has_critical_override = False

        for rule in self.rules:
            res = rule.evaluate(features)
            if res:
                triggered_results.append(res)
                total_impact += res.impact
                if res.is_critical_override:
                    has_critical_override = True

        rules_score = min(100.0, total_impact)
        return rules_score, triggered_results, has_critical_override
