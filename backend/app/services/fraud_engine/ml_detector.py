import os
import joblib
import numpy as np
from typing import List
from sklearn.ensemble import IsolationForest
from app.services.fraud_engine.feature_extractor import TransactionFeatureVector

MODEL_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "ml", "models")
MODEL_PATH = os.path.abspath(os.path.join(MODEL_DIR, "isolation_forest.joblib"))

class MLAnomalyDetector:
    def __init__(self, model_path: str = MODEL_PATH):
        self.model_path = model_path
        self.model: IsolationForest = self._load_or_train_model()

    def _generate_synthetic_training_data(self) -> np.ndarray:
        """Generates 2,000 synthetic transaction feature vectors for baseline IsolationForest training."""
        np.random.seed(42)
        n_samples = 2000

        # 95% Normal activity (1,900 samples)
        amounts_normal = np.random.exponential(scale=200, size=1900) + 10  # $10 - $1,000 range
        velocity_normal = np.random.poisson(lam=0.5, size=1900)
        seconds_normal = np.random.exponential(scale=3600, size=1900) + 30
        balance_ratio_normal = np.random.beta(a=1, b=10, size=1900) * 0.3
        hours_normal = np.random.randint(7, 23, size=1900)

        normal_vectors = np.column_stack((
            amounts_normal,
            velocity_normal,
            seconds_normal,
            balance_ratio_normal,
            hours_normal
        ))

        # 5% Anomalous activity (100 samples)
        amounts_anomalous = np.random.uniform(5000, 25000, size=100)
        velocity_anomalous = np.random.randint(4, 15, size=100)
        seconds_anomalous = np.random.uniform(1, 20, size=100)
        balance_ratio_anomalous = np.random.uniform(0.85, 1.0, size=100)
        hours_anomalous = np.random.randint(0, 6, size=100)

        anomalous_vectors = np.column_stack((
            amounts_anomalous,
            velocity_anomalous,
            seconds_anomalous,
            balance_ratio_anomalous,
            hours_anomalous
        ))

        return np.vstack((normal_vectors, anomalous_vectors))

    def _load_or_train_model(self) -> IsolationForest:
        os.makedirs(os.path.dirname(self.model_path), exist_ok=True)
        if os.path.exists(self.model_path):
            try:
                model = joblib.load(self.model_path)
                return model
            except Exception:
                pass  # Fallback to train if file corrupted

        # Train new IsolationForest model
        X_train = self._generate_synthetic_training_data()
        model = IsolationForest(
            n_estimators=100,
            contamination=0.05,
            random_state=42
        )
        model.fit(X_train)
        joblib.dump(model, self.model_path)
        return model

    def predict_risk_score(self, features: TransactionFeatureVector) -> float:
        """
        Predicts anomaly score and normalizes to 0-100 risk score range.
        decision_function returns positive for inliers (normal) and negative for outliers (anomalous).
        """
        vector = np.array([features.to_list()])
        decision_score = self.model.decision_function(vector)[0]

        # Normalization mapping: decision_score 0.20 -> 0.0 risk, -0.30 -> 100.0 risk
        risk_score = (0.20 - decision_score) * 200.0
        return float(max(0.0, min(100.0, round(risk_score, 2))))

