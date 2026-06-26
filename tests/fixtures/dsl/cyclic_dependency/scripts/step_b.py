"""Step B placeholder."""
import json, os
os.makedirs("results", exist_ok=True)
with open("results/b.json", "w") as f:
    json.dump({"step": "b"}, f)
