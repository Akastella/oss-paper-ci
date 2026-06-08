"""Training script."""
import argparse
import random

random.seed(42)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", required=True)
    args = parser.parse_args()
    print(f"Training with {args.config}")

if __name__ == "__main__":
    main()