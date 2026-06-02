# ============================================================
# anomaly_model.py — Loads the trained model and runs predictions
# This is the bridge between the saved .pkl file and the API
#
# Used by routes/predict.py and routes/websocket.py
# ============================================================

import joblib
import numpy as np
import json
import os
from app.logger import log

# Global model and scaler — loaded once on startup
model = None
scaler = None
features = None

def load_model():
    """
    Load the trained model from disk.
    Called once when FastAPI starts up (in main.py lifespan).
    """
    global model, scaler, features

    model_path = "ml/models/isolation_forest.pkl"
    scaler_path = "ml/models/scaler.pkl"
    features_path = "ml/models/features.json"

    # Check if model exists
    if not os.path.exists(model_path):
        log.warning("No trained model found. Run ml/train.py first.")
        log.warning("Using dummy prediction logic until model is trained.")
        return False

    try:
        model = joblib.load(model_path)
        scaler = joblib.load(scaler_path)
        with open(features_path) as f:
            features = json.load(f)

        log.info("Anomaly detection model loaded successfully.")
        return True

    except Exception as e:
        log.error(f"Failed to load model: {e}")
        return False


def predict(temperature: float, spindle_speed: float,
            vibration: float = 0.3, power_consumption: float = 500.0):
    """
    Run anomaly detection on a single telemetry reading.

    Returns:
        anomaly (bool): True if anomaly detected
        score (float): 0.0 = normal, 1.0 = definitely anomaly
        confidence (str): "low", "medium", "high"
    """
    global model, scaler

    # If model not loaded — fall back to simple rule
    if model is None or scaler is None:
        is_anomaly = temperature > 90.0
        score = min((temperature - 60) / 40, 1.0) if is_anomaly else 0.1
        return is_anomaly, round(score, 3), "rule-based"

    try:
        # Prepare input — must match training feature order
        X = np.array([[temperature, spindle_speed, vibration, power_consumption]])

        # Scale input same way training data was scaled
        X_scaled = scaler.transform(X)

        # Predict — returns 1 (normal) or -1 (anomaly)
        prediction = model.predict(X_scaled)[0]
        is_anomaly = prediction == -1

        # Get anomaly score — lower = more anomalous
        raw_score = model.score_samples(X_scaled)[0]

        # Convert to 0-1 scale where 1 = most anomalous
        # Typical scores range from -0.5 to 0.5
        normalized_score = max(0.0, min(1.0, (-raw_score + 0.5) / 1.0))

        # Confidence level
        if normalized_score > 0.7:
            confidence = "high"
        elif normalized_score > 0.4:
            confidence = "medium"
        else:
            confidence = "low"

        return is_anomaly, round(normalized_score, 3), confidence

    except Exception as e:
        log.error(f"Prediction error: {e}")
        # Fallback to rule-based
        is_anomaly = temperature > 90.0
        score = 0.9 if is_anomaly else 0.1
        return is_anomaly, score, "rule-based"


def is_model_loaded():
    """Check if model is ready."""
    return model is not None
