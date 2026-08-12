import pytest
from decimal import Decimal
from app.models.user import User
from app.services.fraud_engine.feature_extractor import TransactionFeatureVector
from app.services.fraud_engine.rules_engine import RulesEngine

def test_high_amount_rule():
    engine = RulesEngine()

    # Normal amount < $5,000
    features_normal = TransactionFeatureVector(amount=500.0, velocity_5m=0, seconds_since_last_tx=3600.0, balance_ratio=0.05, hour_of_day=14)
    score, rules, override = engine.evaluate(features_normal)
    assert score == 0.0
    assert len(rules) == 0
    assert not override

    # Elevated amount $6,000
    features_elevated = TransactionFeatureVector(amount=6000.0, velocity_5m=0, seconds_since_last_tx=3600.0, balance_ratio=0.6, hour_of_day=14)
    score, rules, override = engine.evaluate(features_elevated)
    assert score == 40.0
    assert len(rules) == 1
    assert rules[0].rule_name == "HIGH_AMOUNT_ELEVATED"
    assert not override

    # Critical amount $12,000
    features_critical = TransactionFeatureVector(amount=12000.0, velocity_5m=0, seconds_since_last_tx=3600.0, balance_ratio=0.8, hour_of_day=14)
    score, rules, override = engine.evaluate(features_critical)
    assert score == 85.0
    assert rules[0].rule_name == "HIGH_AMOUNT_CRITICAL"
    assert override

def test_high_velocity_and_rapid_succession_rules():
    engine = RulesEngine()

    features = TransactionFeatureVector(
        amount=100.0,
        velocity_5m=5,  # > 3
        seconds_since_last_tx=10.0,  # < 30s
        balance_ratio=0.01,
        hour_of_day=10
    )
    score, rules, override = engine.evaluate(features)
    assert score == 65.0  # 35 + 30
    assert len(rules) == 2
    rule_names = [r.rule_name for r in rules]
    assert "HIGH_VELOCITY" in rule_names
    assert "RAPID_SUCCESSION" in rule_names

def test_account_drain_rule():
    engine = RulesEngine()

    features = TransactionFeatureVector(
        amount=9500.0,
        velocity_5m=0,
        seconds_since_last_tx=86400.0,
        balance_ratio=0.95,  # > 0.90
        hour_of_day=12
    )
    score, rules, override = engine.evaluate(features)
    # Triggers High Amount Elevated (+40) and Account Drain (+25) = 65
    assert score == 65.0
    rule_names = [r.rule_name for r in rules]
    assert "ACCOUNT_DRAIN" in rule_names
