"""Training script for Transformer model."""
import argparse
import random
import yaml
import numpy as np

def set_seed(seed: int):
    random.seed(seed)
    np.random.seed(seed)
    try:
        import torch
        torch.manual_seed(seed)
    except ImportError:
        pass

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", required=True)
    args = parser.parse_args()

    with open(args.config) as f:
        config = yaml.safe_load(f)

    set_seed(config["training"]["seed"])
    print(f"Training with config: {args.config}")
    print(f"Model: d_model={config['model']['d_model']}")

if __name__ == "__main__":
    main()
