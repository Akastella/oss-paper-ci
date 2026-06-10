"""Train a toy model and save metrics.

This script demonstrates a minimal reproducible experiment.
It does NOT require network access or real data.
"""
import json
import os
import random

# Fixed seed for reproducibility
random.seed(42)

os.makedirs("results", exist_ok=True)

# Simulate training
print("Starting training...")
epochs = 10
loss_values = []
for epoch in range(1, epochs + 1):
    loss = 1.0 / epoch + random.uniform(-0.01, 0.01)
    loss_values.append(round(loss, 4))
    print(f"  Epoch {epoch}/{epochs} — loss: {loss_values[-1]:.4f}")

accuracy = 0.85 + 0.01 * epochs + random.uniform(-0.005, 0.005)
metrics = {
    "accuracy": round(accuracy, 4),
    "final_loss": loss_values[-1],
    "epochs": epochs,
    "loss_curve": loss_values,
    "seed": 42,
}

with open("results/metrics.json", "w") as f:
    json.dump(metrics, f, indent=2)

print(f"\nTraining complete. Accuracy: {metrics['accuracy']:.4f}")
print("Metrics saved to results/metrics.json")
