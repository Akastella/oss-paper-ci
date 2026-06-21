"""Demo training script.

Generates deterministic model artifacts using only the standard library.
No external dependencies. No network access. Completes in under 1 second.
"""

import json
import os
from pathlib import Path

# Ensure output directories exist
Path("results").mkdir(exist_ok=True)

# Generate deterministic model
model = {
    "type": "demo-classifier",
    "version": "1.0",
    "features": ["x1", "x2"],
    "weights": [0.5, 0.3],
    "bias": 0.1,
    "seed": 42,
}

with open("results/model.json", "w") as f:
    json.dump(model, f, indent=2)

# Generate deterministic training metrics
train_metrics = {
    "epoch": 10,
    "train_loss": 0.234,
    "train_accuracy": 0.89,
    "seed": 42,
}

with open("results/train_metrics.json", "w") as f:
    json.dump(train_metrics, f, indent=2)

print("Training complete.")
print(f"  Model: results/model.json")
print(f"  Metrics: results/train_metrics.json")
