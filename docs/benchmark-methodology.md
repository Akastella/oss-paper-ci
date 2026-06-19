# Benchmark Methodology

This document describes how oss-paper-ci's evaluation benchmark is designed and validated.

## Goals

1. **Stability**: Verify consistent output across runs
2. **Coverage**: Test diverse repository states and languages
3. **Safety**: Ensure no dangerous execution during evaluation
4. **Transparency**: Clear documentation of what is tested

## Non-Goals

- Proving scientific correctness of papers
- Covering every real-world repository type
- Measuring absolute performance metrics
- Comparing with other tools

## Design Process

### 1. Defect Taxonomy

Common reproducibility issues are categorized:

| Category | Examples |
|----------|----------|
| Missing Environment | No requirements.txt, no Dockerfile |
| Missing Data | No data documentation, no availability statement |
| Bad Results | Invalid JSON, missing artifacts |
| Unsafe Scripts | curl\|bash, eval(), rm -rf |
| Weak Provenance | No CITATION.cff, no license |

### 2. Fixture Design

Each fixture is designed to:
- Represent a specific defect combination
- Use minimal synthetic code (print statements only)
- Include clear documentation of intended behavior
- Have defined expected outcomes

### 3. Expected Outcomes

Each fixture has an entry in `expected_outcomes.yml` specifying:
- Ecosystems to detect
- Expected status
- Score band (acceptable range)
- Expected findings
- Expected risks

### 4. Evaluation Process

For each repository in the corpus:

1. **Ecosystem Detection**: Identify language/tool ecosystems
2. **Scan**: Run oss-paper-ci scan (read-only)
3. **Compare**: Match actual vs expected outcomes
4. **Report**: Generate pass/fail/warn summary

### 5. Golden Regression

Golden files capture expected output for regression testing:
- `tests/golden/evaluation_summary.json`
- `tests/golden/evaluation_matrix.md`

Updated via: `python scripts/update_evaluation_golden.py`

## Validation

### What We Validate

- Ecosystem detection accuracy
- Status classification
- Score band compliance
- Finding detection
- Risk identification

### What We Don't Validate

- Scientific correctness
- Real-world applicability
- Performance benchmarks
- Cross-tool comparisons

## Reproducibility

To reproduce evaluation results:

```bash
# Install package
pip install -e ".[dev]"

# Run evaluation
oss-paper-ci eval run examples/evaluation-corpus --format json --output result.json

# Compare with golden
oss-paper-ci eval compare \
  --baseline tests/golden/evaluation_summary.json \
  --current result.json
```

## Adding New Tests

When adding new evaluation fixtures:

1. Design fixture with specific defect combination
2. Define expected outcomes
3. Run evaluation to establish baseline
4. Update golden files
5. Document in this file

## Limitations

- Synthetic fixtures may not capture every real-world complexity
- Score bands are approximate, not absolute
- Ecosystem detection depends on file patterns
- No network access during evaluation
