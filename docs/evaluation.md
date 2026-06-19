# Evaluation

oss-paper-ci includes a **synthetic-but-realistic evaluation corpus** to verify output stability across different repository states.

## Overview

The evaluation corpus is a collection of 12+ synthetic test repositories designed to cover common reproducibility scenarios. These are **not real-world repositories** — they are carefully crafted fixtures that mimic realistic repository structures and issues.

## Running Evaluations

### Basic Usage

```bash
# Run evaluation against the corpus
oss-paper-ci eval run examples/evaluation-corpus

# Output as JSON
oss-paper-ci eval run examples/evaluation-corpus --format json

# Output as HTML
oss-paper-ci eval run examples/evaluation-corpus --format html

# Save to file
oss-paper-ci eval run examples/evaluation-corpus --format json --output report.json
```

### Comparing Against Baseline

```bash
# Compare current results against golden baseline
oss-paper-ci eval compare \
  --baseline tests/golden/evaluation_summary.json \
  --current examples/reports/evaluation_summary.json
```

## Corpus Contents

The evaluation corpus includes repositories covering:

| Category | Repositories | Description |
|----------|--------------|-------------|
| Python | python_good_repro, python_missing_data, python_missing_environment, python_bad_results | Various Python reproducibility states |
| R | r_repro_project | R project with renv |
| Julia | julia_project | Julia project with Project.toml |
| Node.js | node_analysis_project | Node.js analysis project |
| Make | make_workflow_project | Make-based workflow |
| Snakemake | snakemake_project | Snakemake workflow |
| C++ | cpp_build_project | C++ build project |
| Safety | unsafe_script_project | Tests dry-run detection |
| Adoption | adoption_before_after | Before/after comparison |

## Expected Outcomes

Each repository has an `expected_outcomes.yml` entry specifying:
- Expected ecosystems to detect
- Expected status (good/needs-work/critical)
- Expected score band
- Expected findings and risks

## Interpreting Results

- **Pass**: All expectations met
- **Partial**: Some expectations met
- **Fail**: No expectations met
- **Evaluated**: No expectations defined (informational only)

## Limitations

- Corpus uses synthetic fixtures, not real repositories
- Results demonstrate tool stability, not scientific correctness
- Does not cover every possible repository state
- Default mode is scan-only (no script execution)

## Golden Regression

Golden files in `tests/golden/` provide baseline expectations. Update them with:

```bash
python scripts/update_evaluation_golden.py
```

## Methodology

See [Benchmark Methodology](benchmark-methodology.md) for details on how evaluations are designed and validated.
