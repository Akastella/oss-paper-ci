# Reproducibility DSL

The Reproducibility DSL is a YAML-based schema for declaring how to reproduce a
research paper's computational results.  It replaces implicit command guessing
with explicit step declarations, forming a directed acyclic graph (DAG) that the
tool can validate, visualize, and plan -- but never auto-execute.

## Why a DSL?

Legacy `reproducibility.yml` files (v0.2/v0.3) used flat experiment lists with
no formal dependency ordering.  The DSL v1 schema adds:

- **Explicit steps** -- every command is declared, not inferred.
- **Dependency graph** -- steps declare `needs` to form a DAG.
- **Safety declarations** -- network, install, and GPU requirements are stated
  up front and checked before any execution is considered.
- **Deterministic normalization** -- the same YAML always produces the same
  canonical JSON, enabling diff and hash comparison.

## Quick start

```bash
# Validate a DSL file
oss-paper-ci dsl validate reproducibility.yml

# Normalize to canonical v1 JSON
oss-paper-ci dsl normalize reproducibility.yml --format json

# Visualize the dependency graph
oss-paper-ci dsl graph reproducibility.yml --output dag.dot

# Generate an execution plan (dry-run by default)
oss-paper-ci dsl plan reproducibility.yml --format markdown

# Human-readable explanation of the DAG
oss-paper-ci dsl explain reproducibility.yml --format markdown

# Migrate a legacy config
oss-paper-ci dsl migrate OLD.yml --output new.yml
```

All commands default to dry-run mode.  No code is executed, no packages are
installed, and no network access is performed.

## CLI commands

| Command       | Purpose                                      | Default format |
|---------------|----------------------------------------------|----------------|
| `validate`    | Check schema, dependencies, paths, safety    | markdown       |
| `normalize`   | Convert to canonical v1 JSON                 | json           |
| `graph`       | Output DAG in Graphviz DOT format            | dot            |
| `plan`        | Generate ordered execution plan              | markdown       |
| `explain`     | Human-readable DAG report                    | markdown       |
| `migrate`     | Convert legacy v0.2/v0.3 to v1              | json           |

Every command accepts `--format json|markdown|html` (where applicable) and
`--output FILE` to write results to a file instead of stdout.

## File structure

A minimal `reproducibility.yml` v1 file:

```yaml
version: 1

project:
  name: my-paper

environments:
  default:
    adapter: python
    python: ">=3.10"
    install:
      - requirements.txt

datasets:
  input-data:
    path: data/
    required: true

steps:
  train:
    command: python scripts/train.py
    adapter: python
    needs: []
    produces:
      - results/model.json
    timeout: 600

artifacts:
  - results/model.json

safety:
  network: false
  allow_install: false
  allow_gpu: false
```

See [Reproducibility Schema v1](reproducibility-schema-v1.md) for the full
reference.

## How it works

1. **Load** -- the loader reads YAML and auto-detects the schema version
   (v1, v0.2, or v0.3).  Legacy formats are converted transparently.
   See [Migrating from Legacy Formats](dsl-migration.md).

2. **Validate** -- the validator checks schema structure, dependency integrity,
   path safety, metric bounds, and environment references.

3. **Build DAG** -- steps are assembled into a directed acyclic graph.  Cycle
   detection (Kahn's algorithm), topological sort, parallel group identification,
   and critical path analysis are performed.
   See [DAG Planner](dag-planner.md).

4. **Safety check** -- each step command is scanned against blocked patterns
   (e.g., `sudo`, `rm -rf /`, `curl | sh`), undeclared network/install
   operations, and secret exposure.
   See [DSL Safety](dsl-safety.md).

5. **Plan** -- an execution plan is produced listing steps in topological order
   with parallel group assignments, timeout estimates, and blocked/skipped
   status.  The plan is always a dry-run; it describes what *would* happen
   without actually running anything.

## Key concepts

### Steps form a DAG

Each step declares its dependencies via `needs`.  The tool resolves the
topological order automatically:

```
preprocess --> train --> evaluate --> visualize
```

Steps at the same depth can run in parallel.  The tool identifies these parallel
groups and reports the critical path (longest weighted path by timeout).

### Safety defaults to restrictive

All safety flags default to `false`:

- `network: false` -- steps may not access the network.
- `allow_install: false` -- steps may not install packages at runtime.
- `allow_gpu: false` -- steps may not request GPU resources.

If a step command contains `pip install` but `allow_install` is `false`, a
warning is raised.  Commands matching blocked patterns (e.g., `sudo`, `rm -rf /`)
are always blocked regardless of settings.

### The tool never auto-executes

All DSL commands are read-only analysis tools.  They validate, normalize,
visualize, and plan -- but they do not execute reproduction steps.  Actual
execution requires an explicit user action (e.g., `oss-paper-ci reproduce .`).

## Related documentation

- [Reproducibility Schema v1](reproducibility-schema-v1.md) -- full schema reference
- [DAG Planner](dag-planner.md) -- how dependency resolution works
- [DSL Safety](dsl-safety.md) -- safety checks and declarations
- [DSL Migration](dsl-migration.md) -- migrating from legacy formats
- [DSL Examples](dsl-examples.md) -- usage examples
- [DSL GitHub Actions](dsl-github-actions.md) -- CI/CD integration
