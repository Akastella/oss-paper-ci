"""Evaluate step placeholder."""
import json, os
os.makedirs("results", exist_ok=True)
with open("results/metrics.json", "w") as f:
    json.dump({"accuracy": 0.85}, f)
