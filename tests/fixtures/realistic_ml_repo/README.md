# Attention Is All You Need (Reproduction)

PyTorch reproduction of the Transformer model from Vaswani et al. (2017).

## Installation

```bash
pip install -r requirements.txt
pip install -e .
```

## Quick Start

```bash
# Smoke test (runs in ~1 minute)
python scripts/train.py --config configs/smoke.yml

# Full training
python scripts/train.py --config configs/default.yml

# Evaluate
python scripts/evaluate.py --checkpoint results/checkpoints/best.pt

# Generate figures
python scripts/make_figures.py
```

## Data

Download the WMT14 En-De dataset:
```bash
python scripts/download_data.py
```

Or manually download from https://example.com/wmt14 and place in `data/raw/`.

## Reproducing Results

1. Download data: `python scripts/download_data.py`
2. Train: `python scripts/train.py --config configs/default.yml`
3. Evaluate: `python scripts/evaluate.py`
4. Figures: `python scripts/make_figures.py`

See `paper/main.tex` for the full paper.

## Citation

```bibtex
@article{transformer2017,
  title={Attention Is All You Need},
  author={Vaswani, Ashish and others},
  year={2017}
}
```

## License

MIT
