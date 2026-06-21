"""Demo figure generation script.

Generates a text-based figure placeholder using only the standard library.
No external dependencies. No network access. Completes in under 1 second.
"""

import json
from pathlib import Path

# Ensure output directories exist
Path("figures").mkdir(exist_ok=True)

# Load metrics for the summary
try:
    with open("results/metrics.json") as f:
        metrics = json.load(f)
except FileNotFoundError:
    metrics = {"accuracy": 0.0, "loss": 0.0}

# Generate text-based summary figure
summary = f"""
========================================
  Demo Model Summary
========================================
  Accuracy:  {metrics.get('accuracy', 'N/A')}
  Loss:      {metrics.get('loss', 'N/A')}
  Precision: {metrics.get('precision', 'N/A')}
  Recall:    {metrics.get('recall', 'N/A')}
  F1:        {metrics.get('f1', 'N/A')}
========================================
  Seed: 42 (deterministic)
========================================
"""

with open("figures/summary.txt", "w") as f:
    f.write(summary)

print("Figure generation complete.")
print(f"  Summary: figures/summary.txt")
