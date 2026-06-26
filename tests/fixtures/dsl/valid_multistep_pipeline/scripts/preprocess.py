"""Preprocess step placeholder."""
import json, os
os.makedirs("results", exist_ok=True)
with open("results/preprocessed.json", "w") as f:
    json.dump({"status": "preprocessed"}, f)
