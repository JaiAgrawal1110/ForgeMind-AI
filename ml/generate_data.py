# ============================================================
# generate_data.py — Creates fake CNC telemetry data
# We need training data for our model
# Normal data: machine running fine
# Anomalous data: machine about to fail
#
# Run this first before training:
# python ml/generate_data.py
# ============================================================

import pandas as pd
import numpy as np
import os

# Set seed so results are reproducible
np.random.seed(42)

def generate_normal_data(n_samples=1000):
    """
    Generate normal operating data.
    These are readings when machines are healthy.
    """
    data = {
        # Temperature: normally 60-80°C
        "temperature": np.random.normal(70, 5, n_samples),

        # Spindle speed: normally 1000-3000 RPM
        "spindle_speed": np.random.normal(2000, 300, n_samples),

        # Vibration: low when healthy
        "vibration": np.random.normal(0.3, 0.05, n_samples),

        # Power consumption: stable when healthy (watts)
        "power_consumption": np.random.normal(500, 30, n_samples),
    }
    df = pd.DataFrame(data)
    df["label"] = 0    # 0 = normal
    return df


def generate_anomalous_data(n_samples=100):
    """
    Generate anomalous data — machines behaving badly.
    3 types of failures:
    1. Overheating — temperature spikes
    2. Spindle fault — speed drops or spikes
    3. Bearing failure — high vibration
    """

    anomalies = []

    # Type 1: Overheating (temp > 90°C)
    n = n_samples // 3
    overheating = {
        "temperature": np.random.normal(95, 5, n),       # Way too hot
        "spindle_speed": np.random.normal(2000, 300, n), # Speed normal
        "vibration": np.random.normal(0.4, 0.1, n),      # Slightly high
        "power_consumption": np.random.normal(650, 50, n) # Higher power
    }
    anomalies.append(pd.DataFrame(overheating))

    # Type 2: Spindle fault (speed way off)
    spindle_fault = {
        "temperature": np.random.normal(75, 5, n),
        "spindle_speed": np.random.normal(500, 100, n),  # Way too slow
        "vibration": np.random.normal(0.8, 0.2, n),      # High vibration
        "power_consumption": np.random.normal(400, 50, n)
    }
    anomalies.append(pd.DataFrame(spindle_fault))

    # Type 3: Bearing failure (extreme vibration)
    bearing_failure = {
        "temperature": np.random.normal(80, 8, n),
        "spindle_speed": np.random.normal(1800, 400, n),
        "vibration": np.random.normal(2.0, 0.5, n),      # Extremely high
        "power_consumption": np.random.normal(580, 80, n)
    }
    anomalies.append(pd.DataFrame(bearing_failure))

    df = pd.concat(anomalies, ignore_index=True)
    df["label"] = 1    # 1 = anomaly
    return df


def generate_and_save():
    """Generate full dataset and save to CSV."""
    print("Generating normal data...")
    normal = generate_normal_data(1000)

    print("Generating anomalous data...")
    anomalous = generate_anomalous_data(100)

    # Combine both
    full_dataset = pd.concat([normal, anomalous], ignore_index=True)

    # Shuffle so normal and anomalous are mixed
    full_dataset = full_dataset.sample(frac=1, random_state=42).reset_index(drop=True)

    # Save to CSV
    os.makedirs("ml/data", exist_ok=True)
    full_dataset.to_csv("ml/data/telemetry_data.csv", index=False)

    print(f"Dataset saved: {len(full_dataset)} rows")
    print(f"Normal: {len(normal)} | Anomalous: {len(anomalous)}")
    print("File: ml/data/telemetry_data.csv")

    return full_dataset


if __name__ == "__main__":
    generate_and_save()
