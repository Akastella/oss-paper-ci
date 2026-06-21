# Reproduction Run Report

**Version:** 3.1.0rc1
**Status:** success
**Dry run:** No
**Started:** 2026-06-21T01:36:41Z
**Finished:** 
**Sandbox:** local

## Command Results

| ID | Command | Status | Exit | Duration |
|-----|---------|--------|------|----------|
| `train` | `python scripts/train.py` | ✅ success | 0 | 0.1s |
| `evaluate` | `python scripts/evaluate.py` | ✅ success | 0 | 0.1s |
| `make_figures` | `python scripts/make_figures.py` | ✅ success | 0 | 0.1s |

### train

<details><summary>stdout</summary>

```
Training complete.
  Model: results/model.json
  Metrics: results/train_metrics.json

```
</details>

### evaluate

<details><summary>stdout</summary>

```
Evaluation complete.
  Accuracy: 0.87
  Loss: 0.312
  Metrics: results/metrics.json

```
</details>

### make_figures

<details><summary>stdout</summary>

```
Figure generation complete.
  Summary: figures/summary.txt

```
</details>

## Artifacts

- **Expected:** 4
- **Found:** 4
- **Missing:** 0

| Path | Exists | Size | SHA256 |
|------|--------|------|--------|
| `results/model.json` | ✅ | 170 | 4ac2542d0a1c6b13... |
| `results/train_metrics.json` | ✅ | 85 | a1d042bc38485525... |
| `results/metrics.json` | ✅ | 137 | f160814154cec268... |
| `figures/summary.txt` | ✅ | 316 | e53b998406ff5d54... |

## Metrics

- **Checked:** 2
- **In range:** 2
- **Out of range:** 0
- **Errors:** 0

| Key | Value | Min | Max | Status |
|-----|-------|-----|-----|--------|
| `accuracy` | 0.87 | 0.0 | 1.0 | ✅ |
| `loss` | 0.312 | 0.0 | — | ✅ |

---

*This report documents an attempted reproduction run. It does not prove scientific correctness or guarantee reproducibility.*