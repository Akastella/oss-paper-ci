# Demo Reproduce Repository

A minimal example of a scientific paper repository for testing the
`oss-paper-ci reproduce` command. This is a toy project, not real research.

## Setup

```bash
pip install -r requirements.txt
```

## Reproduce

```bash
python scripts/train.py
python scripts/evaluate.py
python scripts/make_figures.py
```

## Results

- `results/metrics.json` — training metrics
- `figures/accuracy_curve.txt` — accuracy over epochs

## License

MIT
