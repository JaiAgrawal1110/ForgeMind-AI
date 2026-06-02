# ============================================================
# train.py — Trains the Isolation Forest anomaly detection model
#
# Isolation Forest works by:
# - Randomly isolating data points
# - Anomalies are isolated faster (fewer splits needed)
# - Normal points take more splits to isolate
# No labels needed — purely unsupervised learning
#
# Run after generate_data.py:
# python ml/train.py
# ============================================================

import pandas as pd
import numpy as np
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import classification_report
import joblib
import os
import json

# Features we train on — must match what the API sends
FEATURES = ["temperature", "spindle_speed", "vibration", "power_consumption"]

def load_data():
    """Load the generated telemetry dataset."""
    path = "ml/data/telemetry_data.csv"
    if not os.path.exists(path):
        raise FileNotFoundError("Run generate_data.py first!")
    df = pd.read_csv(path)
    print(f"Loaded {len(df)} rows")
    return df


def train_model(df):
    """
    Train Isolation Forest on normal data only.
    This is unsupervised — we only show it normal examples.
    It learns what normal looks like, then flags anything different.
    """
    # Separate normal and anomalous data
    normal_data = df[df["label"] == 0][FEATURES]
    print(f"Training on {len(normal_data)} normal samples...")

    # Scale features — important for Isolation Forest
    # StandardScaler converts all features to same scale (mean=0, std=1)
    scaler = StandardScaler()
    normal_scaled = scaler.fit_transform(normal_data)

    # Train Isolation Forest
    # contamination = expected % of anomalies in real data (we estimate 5%)
    model = IsolationForest(
        n_estimators=100,      # Number of trees
        contamination=0.05,    # Expected anomaly rate
        random_state=42,
        n_jobs=-1              # Use all CPU cores
    )
    model.fit(normal_scaled)
    print("Model trained!")

    return model, scaler


def evaluate_model(model, scaler, df):
    """
    Test the model on both normal and anomalous data.
    Shows how well it detects real anomalies.
    """
    X = df[FEATURES]
    X_scaled = scaler.transform(X)
    y_true = df["label"]

    # Isolation Forest returns: 1 = normal, -1 = anomaly
    # We convert to: 0 = normal, 1 = anomaly
    predictions = model.predict(X_scaled)
    y_pred = (predictions == -1).astype(int)

    print("\n--- Model Evaluation ---")
    print(classification_report(y_true, y_pred, target_names=["Normal", "Anomaly"]))

    # Anomaly scores — lower = more anomalous
    scores = model.score_samples(X_scaled)
    print(f"Score range: {scores.min():.3f} to {scores.max():.3f}")

    return y_pred


def save_model(model, scaler):
    """Save model and scaler to disk."""
    os.makedirs("ml/models", exist_ok=True)

    # Save model
    joblib.dump(model, "ml/models/isolation_forest.pkl")
    print("Model saved: ml/models/isolation_forest.pkl")

    # Save scaler
    joblib.dump(scaler, "ml/models/scaler.pkl")
    print("Scaler saved: ml/models/scaler.pkl")

    # Save feature names so we know what order to use
    with open("ml/models/features.json", "w") as f:
        json.dump(FEATURES, f)
    print("Features saved: ml/models/features.json")


if __name__ == "__main__":
    # Step 1: Load data
    df = load_data()

    # Step 2: Train model
    model, scaler = train_model(df)

    # Step 3: Evaluate
    evaluate_model(model, scaler, df)

    # Step 4: Save
    save_model(model, scaler)

    print("\nDone! Now update routes/predict.py to use the real model.")
