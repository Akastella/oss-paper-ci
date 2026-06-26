"""Step A placeholder."""
import json, os
os.makedirs("results", exist_ok=True)
with open("results/a.json", "w") as f:
    json.dump({"step": "a"}, f)
