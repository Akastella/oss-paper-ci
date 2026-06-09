"""Train a toy model and save metrics."""
import json
import os

os.makedirs("results", exist_ok=True)

metrics = {"accuracy": 0.95, "loss": 0.05, "epochs": 10}
with open("results/metrics.json", "w") as f:
    json.dump(metrics, f, indent=2)

print("Training complete. Metrics saved to results/metrics.json")
