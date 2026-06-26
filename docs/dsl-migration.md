# Migrating from Legacy Formats

The DSL system supports automatic migration from legacy `reproducibility.yml`
formats (v0.2 and v0.3) to the current v1 schema.  The migration is read-only
and produces a new file; the original is not modified.

## Supported legacy formats

### v0.3 (contract schema)

The v0.3 format uses `version: "0.3"` with `experiments` lists:

```yaml
version: "0.3"
project_name: demo
project_type: ml
environment:
  type: python
  file: requirements.txt
  python: "3.11"
data:
  - id: demo-data
    path: data/input.csv
    availability: public
experiments:
  - id: train
    command: python scripts/train.py
    timeout_seconds: 3600
    safe_to_run: true
    expected_outputs: [results/model.pkl]
figures:
  - id: loss-curve
    path: figures/loss_curve.png
    generated_by: [train]
```

### v0.2 (orchestrator schema)

The v0.2 format uses `schema_version: "0.2"` with `commands` lists:

```yaml
schema_version: "0.2"
project_name: demo
project_type: ml
commands:
  - id: train
    run: python scripts/train.py
    timeout_seconds: 60
    depends_on: []
    expected_artifacts: [results/model.pkl]
artifacts:
  - path: results/model.pkl
    type: file
metrics:
  - file: results/metrics.json
    key: accuracy
    expected_min: 0.8
    expected_max: 1.0
safety:
  network: false
  allow_shell: false
```

## Migration command

```bash
# Migrate and output v1 JSON
oss-paper-ci dsl migrate OLD.yml --output new.yml

# Migrate and output migration report (markdown)
oss-paper-ci dsl migrate OLD.yml --format markdown --output migration-report.md

# Migrate and output v1 JSON (explicit format)
oss-paper-ci dsl migrate OLD.yml --format json --output new.yml
```

The `--output` flag writes the result to a file.  Without it, the result is
printed to stdout.

## What gets converted

### v0.3 to v1

| v0.3 field              | v1 field                | Notes                              |
|-------------------------|-------------------------|------------------------------------|
| `project_name`          | `project.name`          |                                    |
| `project_type`          | `project.description`   | Stored as `"Type: ml"`             |
| `environment.type`      | `environments.<name>.adapter` |                            |
| `environment.python`    | `environments.<name>.python` |                             |
| `environment.file`      | `environments.<name>.install` | Wrapped in list              |
| `data[]`                | `datasets`              | Each item becomes a named dataset  |
| `experiments[]`         | `steps`                 | Each experiment becomes a step     |
| `experiments[].command` | `steps.*.command`       |                                    |
| `experiments[].timeout_seconds` | `steps.*.timeout` | Renamed field                |
| `experiments[].expected_outputs` | `steps.*.produces` | Renamed field             |
| `figures[]`             | `artifacts[]`           | Type set to `"figure"`             |
| `results[]`             | `artifacts[]`           | Type set to `"metrics"`            |

### v0.2 to v1

| v0.2 field                   | v1 field                | Notes                          |
|------------------------------|-------------------------|--------------------------------|
| `project_name`               | `project.name`          |                                |
| `commands[]`                 | `steps`                 | Each command becomes a step    |
| `commands[].run`             | `steps.*.command`       | Renamed field                  |
| `commands[].timeout_seconds` | `steps.*.timeout`       | Renamed field                  |
| `commands[].depends_on`      | `steps.*.needs`         | Renamed field                  |
| `commands[].expected_artifacts` | `steps.*.produces`  | Renamed field                  |
| `artifacts[]`                | `artifacts[]`           | Preserved                      |
| `metrics[]`                  | `expected.metrics`      | Restructured                   |
| `safety.network`             | `safety.network`        | Preserved                      |

## Migration report

The migration report shows what was converted and any warnings:

```markdown
# Migration Report

**Source version:** v0.3
**Target version:** v1

## Converted

- Steps: 3
- Datasets: 2
- Metrics: 0
- Artifacts: 4

## Warnings

- Some experiments marked safe_to_run=false; review safety settings
```

## Automatic detection

When you run any DSL command on a legacy file, the loader automatically detects
the version and converts it:

```bash
# This works on v0.2, v0.3, or v1 files
oss-paper-ci dsl validate OLD.yml
oss-paper-ci dsl plan OLD.yml
oss-paper-ci dsl explain OLD.yml
```

You do not need to migrate before using these commands.  Migration is only
needed when you want to permanently convert the file to v1 format.

## What is not migrated

Some legacy fields have no direct v1 equivalent:

- `v0.3.project_type` -- stored in `project.description` as a prefix.
- `v0.3.ci` -- CI configuration is not part of the DSL schema.
- `v0.2.safety.allow_shell` -- no direct equivalent; review safety settings.
- `v0.2.safety.max_runtime_seconds` -- per-step timeouts are used instead.
- `v0.2.safety.max_artifact_mb` -- not in v1 schema.
- `v0.3.experiments[].safe_to_run` -- not in v1 schema; use safety flags.

Warnings are emitted for fields that require manual review.

## Example: full migration workflow

```bash
# 1. Check what version the file is
oss-paper-ci dsl validate old-reproducibility.yml

# 2. Generate migration report
oss-paper-ci dsl migrate old-reproducibility.yml \
  --format markdown \
  --output migration-report.md

# 3. Generate new v1 file
oss-paper-ci dsl migrate old-reproducibility.yml \
  --format json \
  --output reproducibility.yml

# 4. Validate the new file
oss-paper-ci dsl validate reproducibility.yml

# 5. Verify the DAG
oss-paper-ci dsl plan reproducibility.yml --format markdown
```

## Related documentation

- [Reproducibility DSL Overview](reproducibility-dsl.md)
- [Reproducibility Schema v1](reproducibility-schema-v1.md)
- [DSL Examples](dsl-examples.md)
