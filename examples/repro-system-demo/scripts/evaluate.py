"""Demo evaluation script.

Generates deterministic evaluation metrics using only the standard library.
No external dependencies. No network access. Completes in under 1 second.
"""

import json
from pathlib import Path

# Ensure output directories exist
Path("results").mkdir(exist_ok=True)

# Generate deterministic evaluation metrics
metrics = {
    "accuracy": 0.87,
    "loss": 0.312,
    "precision": 0.85,
    "recall": 0.89,
    "f1": 0.87,
    "test_samples": 100,
    "seed": 42,
}

with open("results/metrics.json", "w") as f:
    json.dump(metrics, f, indent=2)

print("Evaluation complete.")
print(f"  Accuracy: {metrics['accuracy']}")
print(f"  Loss: {metrics['loss']}")
print(f"  Metrics: results/metrics.json")
