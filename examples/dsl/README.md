# DSL Examples

This directory contains example [Reproducibility DSL v1](../../docs/dsl-v1.md) files
for use with `oss-paper-ci`.

## Files

| File | Description |
|------|-------------|
| `reproducibility.v1.yml` | Complete ML pipeline DSL with preprocessing, training, evaluation, and visualization steps |

## Usage

Validate a DSL file:

```bash
oss-paper-ci dsl validate reproducibility.v1.yml
```

Generate an execution plan (dry-run):

```bash
oss-paper-ci dsl plan reproducibility.v1.yml --format markdown
```

Output the dependency graph in DOT format:

```bash
oss-paper-ci dsl graph reproducibility.v1.yml --output dag.dot
```

Migrate a legacy `reproducibility.yml` to v1:

```bash
oss-paper-ci dsl migrate old-reproducibility.yml --output reproducibility.v1.yml
```

## DSL v1 Schema

The v1 DSL is structured around these top-level keys:

- **version** -- DSL version (must be `1`)
- **project** -- Paper and repository metadata
- **environments** -- Runtime environments (Python, R, etc.)
- **datasets** -- Input data with paths and availability
- **steps** -- Ordered execution steps forming a DAG
- **artifacts** -- Files to preserve after execution
- **expected** -- Metric bounds for pass/fail checks
- **safety** -- Network, install, and GPU restrictions

## Related Workflows

See `examples/github-actions/dsl-*.yml` for CI integration examples:

- `dsl-validate.yml` -- Validate DSL on push/PR
- `dsl-reproduce-dry-run.yml` -- Dry-run reproduction plan
- `dsl-session.yml` -- Session with DSL
- `dsl-matrix.yml` -- Matrix execution with DSL
