"""Evaluation script."""
import json

def main():
    with open("results/metrics.json") as f:
        metrics = json.load(f)
    print(f"Accuracy: {metrics['accuracy']}")

if __name__ == "__main__":
    main()
