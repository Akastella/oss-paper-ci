"""Generate figures from training results."""
import json
import os

os.makedirs("figures", exist_ok=True)

try:
    with open("results/metrics.json") as f:
        metrics = json.load(f)
except FileNotFoundError:
    print("Error: results/metrics.json not found. Run train.py first.")
    exit(1)

# Generate accuracy curve data
loss_curve = metrics.get("loss_curve", [])
with open("figures/accuracy_curve.txt", "w") as f:
    f.write("epoch,loss\n")
    for i, loss in enumerate(loss_curve, 1):
        f.write(f"{i},{loss:.4f}\n")

print(f"Generated figures/accuracy_curve.txt with {len(loss_curve)} data points")
print("Figures saved to figures/")
