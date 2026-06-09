"""Evaluate model and print results."""
import json

try:
    with open("results/metrics.json") as f:
        metrics = json.load(f)
    print(f"Accuracy: {metrics['accuracy']}")
    print(f"Loss: {metrics['loss']}")
except FileNotFoundError:
    print("No metrics found. Run train.py first.")
