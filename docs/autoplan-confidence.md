# Autoplan Confidence Scoring

Confidence scores indicate how well the autoplan can detect repository structure. They do **not** indicate scientific correctness or reproduction success likelihood.

## Score Dimensions

### Environment (weight: 0.3)

How well the environment can be detected:
- +0.3 for detecting any ecosystem
- +0.3 for finding environment files (requirements.txt, pyproject.toml, etc.)
- +0.2 for native support level (Python)
- +0.1 for having an install plan
- +0.1 for runtime availability

### Commands (weight: 0.4)

How confident the extracted commands are:
- +0.2 for finding any commands
- +0.2 for having safe (non-dangerous) commands
- +0.2 for high-confidence commands (≥0.6)
- +0.2 for classified commands (not "unknown")
- +0.1 for multiple command kinds

### Artifacts (weight: 0.2)

How many artifacts were found:
- +0.3 for finding any artifacts
- +0.2 for results directory
- +0.2 for figures directory
- +0.2 for metrics files
- +0.1 for 3+ artifacts

### Metrics (weight: 0.1)

Whether metrics files exist:
- +0.7 for finding metrics files
- +0.3 for finding files with "metric" or "score" in the path

## Overall Score

The overall score is a weighted average:

```
overall = environment × 0.3 + commands × 0.4 + artifacts × 0.2 + metrics × 0.1
```

A +0.1 boost is added if an existing `reproducibility.yml` is found (capped at 1.0).

## Interpretation

| Score | Interpretation |
|-------|---------------|
| 0.8-1.0 | High confidence: good ecosystem detection, multiple commands, artifacts found |
| 0.5-0.8 | Medium confidence: some detection, may need manual review |
| 0.2-0.5 | Low confidence: limited detection, significant manual work needed |
| 0.0-0.2 | Very low confidence: minimal detection, autoplan may not be useful |

## Important

- Confidence scores indicate **detection quality**, not scientific correctness
- A high score does not guarantee the candidate plan is correct
- A low score does not mean the repository is not reproducible
- Always review the candidate plan before execution
