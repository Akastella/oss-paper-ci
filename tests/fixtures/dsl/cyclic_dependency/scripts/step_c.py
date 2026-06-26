"""Step C placeholder."""
import json, os
os.makedirs("results", exist_ok=True)
with open("results/c.json", "w") as f:
    json.dump({"step": "c"}, f)
