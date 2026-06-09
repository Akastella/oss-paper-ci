# Benchmark Fixtures

This directory contains the benchmark fixture matrix, which shows expected
scores and statuses for each test fixture.

## Generating

```bash
python scripts/generate_fixture_matrix.py --format markdown --output examples/benchmark/fixture_matrix.md
python scripts/generate_fixture_matrix.py --format json --output examples/benchmark/fixture_matrix.json
```

## Purpose

The fixture matrix helps verify that scoring behavior is consistent across
releases.  Each fixture represents a different type of repository, and the
expected scores should not change without a deliberate scoring adjustment.

## Fixtures

| Fixture | Description |
|---------|-------------|
| minimal_bad_repo | Minimal repo with almost nothing |
| broken_paper_repo | Paper repo with broken structure |
| paper_ready_repo | Well-structured paper repo |
| realistic_ml_repo | Realistic ML project |
| r_ready_repo | R-based paper repo |
| julia_ready_repo | Julia-based paper repo |
| matlab_minimal_repo | MATLAB-based paper repo |
| make_snakemake_repo | Snakemake workflow repo |
| demo-paper-repo | Example paper repo |

See [docs/benchmark.md](../../docs/benchmark.md) for details.
