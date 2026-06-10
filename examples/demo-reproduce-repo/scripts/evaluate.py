"""Evaluate the trained model and save evaluation metrics."""
import json
import os

os.makedirs("results", exist_ok=True)

try:
    with open("results/metrics.json") as f:
        metrics = json.load(f)
except FileNotFoundError:
    print("Error: results/metrics.json not found. Run train.py first.")
    exit(1)

print(f"Loaded metrics: accuracy={metrics['accuracy']}, loss={metrics['final_loss']}")

# Simulate evaluation
eval_metrics = {
    "test_accuracy": metrics["accuracy"] - 0.02,
    "test_loss": metrics["final_loss"] + 0.01,
    "train_accuracy": metrics["accuracy"],
    "train_loss": metrics["final_loss"],
}

with open("results/eval_metrics.json", "w") as f:
    json.dump(eval_metrics, f, indent=2)

print(f"Test accuracy: {eval_metrics['test_accuracy']:.4f}")
print("Evaluation metrics saved to results/eval_metrics.json")
