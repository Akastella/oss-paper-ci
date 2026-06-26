"""Train step placeholder."""
import json, os
os.makedirs("results", exist_ok=True)
with open("results/model.json", "w") as f:
    json.dump({"model": "dummy"}, f)
