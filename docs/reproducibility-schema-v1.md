# Reproducibility Schema v1 -- Full Reference

This document describes every field in the `reproducibility.yml` DSL v1 schema.

## Top-level structure

```yaml
version: 1          # Required. Must be integer 1.
project: { ... }    # Required.
environments: { }  # Optional. Named environment specs.
datasets: { }      # Optional. Named dataset declarations.
steps: { }          # Required. Named step specs forming a DAG.
artifacts: [ ]      # Optional. Files/dirs to preserve.
expected: { }       # Optional. Metric bounds for pass/fail.
safety: { }         # Optional. Execution safety constraints.
```

---

## `project`

Project metadata.

```yaml
project:
  name: ml-paper-demo            # Required. String.
  description: "Demo pipeline"   # Optional. String.
  paper: "https://arxiv.org/..." # Optional. URL string.
  repository: "https://github.com/..." # Optional. URL string.
```

| Field         | Type   | Required | Description                        |
|---------------|--------|----------|------------------------------------|
| `name`        | string | yes      | Project identifier                 |
| `description` | string | no       | Human-readable description         |
| `paper`       | string | no       | URL to the paper                   |
| `repository`  | string | no       | URL to the source repository       |

---

## `environments`

Named environment specifications.  Each environment declares a language adapter,
runtime, version constraint, and install steps.

```yaml
environments:
  default:
    adapter: python
    runtime: python
    python: ">=3.10"
    install:
      - requirements.txt
  r-env:
    adapter: r
    runtime: R
    install:
      - renv.lock
```

| Field     | Type     | Required | Description                                      |
|-----------|----------|----------|--------------------------------------------------|
| `adapter` | string   | no       | Language adapter name (python, r, julia, etc.)   |
| `runtime` | string   | no       | Runtime identifier                               |
| `python`  | string   | no       | Python version constraint (e.g., `">=3.10"`)     |
| `install` | string[] | no       | Install steps or requirement files               |

Valid adapter names: `python`, `r`, `julia`, `node`, `rust`, `java`, `cpp`,
`make`, `snakemake`, `nextflow`, `shell`, `matlab`.

---

## `datasets`

Named dataset declarations.  Paths are relative to the repository root.

```yaml
datasets:
  training-data:
    path: data/train.csv
    required: true
    description: "Training dataset"
  test-data:
    path: data/test.csv
    required: true
```

| Field         | Type   | Required | Default | Description                          |
|---------------|--------|----------|---------|--------------------------------------|
| `path`        | string | yes      |         | Relative path to the dataset         |
| `required`    | bool   | no       | `true`  | Whether validation fails if missing  |
| `description` | string | no       |         | Human-readable description           |

---

## `steps`

Named step specifications.  Each step defines a command, its dependencies,
outputs, and optional metrics.  The dependency graph must be a DAG (no cycles).

```yaml
steps:
  preprocess:
    command: python scripts/preprocess.py
    adapter: python
    needs: []
    produces:
      - data/processed/
    timeout: 120
    description: "Preprocess raw data"

  train:
    command: python scripts/train.py
    adapter: python
    needs: [preprocess]
    produces:
      - results/model.json
    timeout: 600
    description: "Train the model"

  evaluate:
    command: python scripts/evaluate.py
    adapter: python
    needs: [train]
    produces:
      - results/metrics.json
    timeout: 120
    metrics:
      - path: results/metrics.json
        keys: [accuracy, f1, precision, recall]
    description: "Evaluate model on test set"
```

| Field         | Type       | Required | Default  | Description                              |
|---------------|------------|----------|----------|------------------------------------------|
| `command`     | string     | yes      |          | Shell command to execute                 |
| `adapter`     | string     | no       |          | Language adapter for this step           |
| `needs`       | string[]   | no       | `[]`     | Step IDs this step depends on            |
| `produces`    | string[]   | no       | `[]`     | Paths produced by this step              |
| `timeout`     | int        | no       | `3600`   | Timeout in seconds                       |
| `metrics`     | list       | no       | `[]`     | Metric extraction specs (see below)      |
| `description` | string     | no       |          | Human-readable description               |

### `steps.*.metrics`

Each entry specifies a JSON file and the keys to extract:

```yaml
metrics:
  - path: results/metrics.json
    keys: [accuracy, f1]
```

| Field  | Type     | Required | Description                    |
|--------|----------|----------|--------------------------------|
| `path` | string   | yes      | Path to the metrics JSON file  |
| `keys` | string[] | yes      | Metric keys to extract         |

---

## `artifacts`

Files and directories to preserve after execution.  These are uploaded as CI
artifacts and included in evidence bundles.

```yaml
artifacts:
  - results/metrics.json
  - results/model.json
  - figures/
```

Each entry can be a plain string (path) or an object:

```yaml
artifacts:
  - path: results/metrics.json
    type: metrics
  - path: figures/
    type: figure
```

| Field  | Type   | Required | Default  | Description                              |
|--------|--------|----------|----------|------------------------------------------|
| `path` | string | yes      |          | Relative path to the artifact            |
| `type` | string | no       | `"file"` | Type: file, metrics, figure, table, log  |

---

## `expected`

Expected metric ranges for pass/fail validation.

```yaml
expected:
  metrics:
    accuracy:
      min: 0.80
      max: 1.0
    f1:
      min: 0.75
      max: 1.0
```

| Field  | Type   | Required | Description                    |
|--------|--------|----------|--------------------------------|
| `min`  | float  | no       | Minimum acceptable value       |
| `max`  | float  | no       | Maximum acceptable value       |

If both `min` and `max` are set, the metric must fall within `[min, max]`.

---

## `safety`

Execution safety constraints.  All flags default to the most restrictive
setting (`false`).

```yaml
safety:
  network: false
  allow_install: false
  allow_gpu: false
```

| Field          | Type | Required | Default | Description                          |
|----------------|------|----------|---------|--------------------------------------|
| `network`      | bool | no       | `false` | Whether steps may access the network |
| `allow_install`| bool | no       | `false` | Whether steps may install packages   |
| `allow_gpu`    | bool | no       | `false` | Whether steps may request GPU        |

See [DSL Safety](dsl-safety.md) for details on how these flags are enforced.

---

## Version detection

The loader auto-detects the schema version:

| Version | Detection rule                                              |
|---------|-------------------------------------------------------------|
| v1      | `version: 1` (integer) and `steps` is a mapping             |
| v0.2    | `schema_version: "0.2"` and `commands` is a list            |
| v0.3    | `version: "0.3"` and `experiments` is a list                |

Legacy formats are automatically converted to v1.  See
[DSL Migration](dsl-migration.md).

---

## Canonical normalization

The normalizer produces a stable, deterministic representation:

- All keys are sorted alphabetically.
- All lists are sorted.
- All defaults are explicit.
- Paths are relative (no leading `./`).
- Output is deterministic JSON.

```bash
oss-paper-ci dsl normalize reproducibility.yml --format json --output canonical.json
```

The normalized JSON can be hashed for change detection:

```bash
oss-paper-ci dsl normalize reproducibility.yml --format json | sha256sum
```

---

## Related documentation

- [Reproducibility DSL Overview](reproducibility-dsl.md)
- [DAG Planner](dag-planner.md)
- [DSL Safety](dsl-safety.md)
- [DSL Examples](dsl-examples.md)
