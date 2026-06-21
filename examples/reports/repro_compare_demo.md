# Reproduction Comparison

**Run directory:** `.oss-paper-ci-repro-run`
**Expected:** `examples/repro-system-demo/reproducibility.yml`

**Total:** 6 | **Matched:** 6 | **Mismatched:** 0

## Commands

| Item | Expected | Actual | Status |
|------|----------|--------|--------|
| `train` | success | success | ✅ |
| `evaluate` | success | success | ✅ |
| `make_figures` | success | success | ✅ |

## Artifacts

| Item | Expected | Actual | Status |
|------|----------|--------|--------|
| `results/model.json` | present | present (sha256:4ac2542d0a1c6b13...) | ✅ |
| `results/metrics.json` | present | present (sha256:f160814154cec268...) | ✅ |
| `figures/summary.txt` | present | present (sha256:e53b998406ff5d54...) | ✅ |

---

*This comparison checks declared expectations against observed results. It does not verify scientific correctness.*