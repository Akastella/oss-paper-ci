"""Augment step placeholder."""
import json, os
os.makedirs("results", exist_ok=True)
with open("results/augmented.json", "w") as f:
    json.dump({"augmented": True}, f)
