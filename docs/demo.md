# Demo: Reproducing Example Reports

This guide shows how to generate the same reports included in
`examples/reports/`.

## Prerequisites

```bash
git clone https://github.com/Akastella/oss-paper-ci.git
cd oss-paper-ci
python -m pip install -e ".[dev]"
```

## Generate reports from the test fixture

The `realistic_ml_repo` fixture simulates a well-structured ML paper repository:

```bash
# Scan report (Markdown)
oss-paper-ci scan tests/fixtures/realistic_ml_repo --format markdown

# Scan report (JSON)
oss-paper-ci scan tests/fixtures/realistic_ml_repo --format json

# Evidence graph
oss-paper-ci graph tests/fixtures/realistic_ml_repo --format markdown

# Baseline snapshot
oss-paper-ci baseline create tests/fixtures/realistic_ml_repo --output baseline.json

# Baseline comparison
oss-paper-ci baseline compare tests/fixtures/realistic_ml_repo --baseline baseline.json

# Smoke run (dry-run)
oss-paper-ci smoke tests/fixtures/realistic_ml_repo --dry-run
```

## Generate reports from your own repository

Replace the fixture path with your repository:

```bash
oss-paper-ci scan /path/to/your/repo --format markdown --output report.md
oss-paper-ci graph /path/to/your/repo --format json --output graph.json
oss-paper-ci baseline create /path/to/your/repo --output baseline.json
```

## Example output

See [examples/reports/](../examples/reports/) for pre-generated reports in all
supported formats.

## Fixtures

| Fixture | Description | Expected Score |
|---------|-------------|----------------|
| `realistic_ml_repo` | Well-structured ML project | 90+ |
| `paper_ready_repo` | Paper with good reproducibility setup | 90+ |
| `broken_paper_repo` | Missing LICENSE, incomplete setup | 50-80 |
| `minimal_bad_repo` | Single Python file, no README | 0-30 |
| `r_ready_repo` | R project with renv | 70+ |
| `julia_ready_repo` | Julia project with Project.toml | 50+ |
| `matlab_minimal_repo` | MATLAB project with scripts | 40+ |
| `make_snakemake_repo` | Make/Snakemake project | 50+ |
