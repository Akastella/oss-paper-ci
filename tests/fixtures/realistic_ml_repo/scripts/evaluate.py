"""Evaluation script."""
import argparse

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--checkpoint", default="results/checkpoints/best.pt")
    args = parser.parse_args()
    print(f"Evaluating checkpoint: {args.checkpoint}")

if __name__ == "__main__":
    main()
