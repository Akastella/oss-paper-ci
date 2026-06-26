# DSL Examples

This document shows common `reproducibility.yml` patterns for different project
types.

## Minimal Python pipeline

A simple train/evaluate pipeline:

```yaml
version: 1

project:
  name: simple-ml

environments:
  default:
    adapter: python
    runtime: python
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

  evaluate:
    command: python scripts/evaluate.py
    adapter: python
    needs: [train]
    produces:
      - results/metrics.json
    timeout: 120
    metrics:
      - path: results/metrics.json
        keys: [accuracy, f1]

artifacts:
  - results/metrics.json
  - results/model.json

expected:
  metrics:
    accuracy:
      min: 0.80
      max: 1.0

safety:
  network: false
  allow_install: false
  allow_gpu: false
```

```bash
oss-paper-ci dsl validate reproducibility.yml
oss-paper-ci dsl plan reproducibility.yml --format markdown
```

## Multi-step pipeline with parallel branches

A pipeline where preprocessing branches into feature engineering and
augmentation, which then merge for training:

```yaml
version: 1

project:
  name: parallel-pipeline

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
  preprocess:
    command: python scripts/preprocess.py
    adapter: python
    needs: []
    produces:
      - results/preprocessed.json
    timeout: 30

  feature-engineering:
    command: python scripts/features.py
    adapter: python
    needs: [preprocess]
    produces:
      - results/features.json
    timeout: 30

  augment:
    command: python scripts/augment.py
    adapter: python
    needs: [preprocess]
    produces:
      - results/augmented.json
    timeout: 30

  train:
    command: python scripts/train.py
    adapter: python
    needs: [feature-engineering, augment]
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

```bash
# See the parallel groups
oss-paper-ci dsl plan reproducibility.yml --format markdown

# Visualize the DAG
oss-paper-ci dsl graph reproducibility.yml --output dag.dot
```

## Multi-language pipeline

A pipeline mixing Python and R steps:

```yaml
version: 1

project:
  name: multilang-paper

environments:
  python-env:
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

datasets:
  input-data:
    path: data/
    required: true

steps:
  preprocess:
    command: python scripts/preprocess.py
    adapter: python
    needs: []
    produces:
      - results/clean_data.csv
    timeout: 30

  analyze:
    command: Rscript scripts/analyze.R
    adapter: r
    needs: [preprocess]
    produces:
      - results/analysis.json
    timeout: 60

  visualize:
    command: python scripts/visualize.py
    adapter: python
    needs: [analyze]
    produces:
      - figures/plot.png
    timeout: 30

artifacts:
  - results/analysis.json
  - figures/plot.png

safety:
  network: false
  allow_install: false
  allow_gpu: false
```

## Matrix environments

Test across multiple Python versions:

```yaml
version: 1

project:
  name: matrix-pipeline

environments:
  py310:
    adapter: python
    runtime: python
    python: "3.10"
    install:
      - requirements.txt
  py311:
    adapter: python
    runtime: python
    python: "3.11"
    install:
      - requirements.txt
  py312:
    adapter: python
    runtime: python
    python: "3.12"
    install:
      - requirements.txt

datasets:
  demo-data:
    path: data/
    required: true

steps:
  train:
    command: python scripts/train.py
    adapter: python
    needs: []
    produces:
      - results/model.json
    timeout: 60

  evaluate:
    command: python scripts/evaluate.py
    adapter: python
    needs: [train]
    produces:
      - results/metrics.json
    timeout: 30

artifacts:
  - results/metrics.json

expected:
  metrics:
    accuracy:
      min: 0.0
      max: 1.0

safety:
  network: false
  allow_install: false
  allow_gpu: false
```

```bash
# See all environments
oss-paper-ci dsl validate reproducibility.yml
```

## Steps with optional artifacts

Not every step needs to produce artifacts:

```yaml
version: 1

project:
  name: optional-artifacts

environments:
  default:
    adapter: python
    python: ">=3.10"
    install:
      - requirements.txt

datasets:
  demo-data:
    path: data/
    required: true

steps:
  preprocess:
    command: python scripts/preprocess.py
    adapter: python
    needs: []
    produces: []
    timeout: 30

  train:
    command: python scripts/train.py
    adapter: python
    needs: [preprocess]
    produces:
      - results/model.json
    timeout: 60

  evaluate:
    command: python scripts/evaluate.py
    adapter: python
    needs: [train]
    produces:
      - results/metrics.json
    metrics:
      - path: results/metrics.json
        keys: [accuracy]

  report:
    command: python scripts/report.py
    adapter: python
    needs: [evaluate]
    produces: []
    timeout: 30

artifacts:
  - results/metrics.json
  - figures/

expected:
  metrics:
    accuracy:
      min: 0.0
      max: 1.0

safety:
  network: false
  allow_install: false
  allow_gpu: false
```

## Migrated legacy config

A v0.3 config migrated to v1:

```yaml
version: 1

project:
  name: demo
  description: "Type: ml"

environments:
  python:
    adapter: python
    python: "3.11"
    install:
      - requirements.txt

datasets:
  demo-data:
    path: data/input.csv
    required: true

steps:
  train:
    command: python scripts/train.py
    produces:
      - results/model.pkl

artifacts:
  - path: figures/loss_curve.png
    type: figure

safety:
  network: false
  allow_install: false
  allow_gpu: false
```

## CLI examples

```bash
# Validate
oss-paper-ci dsl validate reproducibility.yml

# Validate with JSON output
oss-paper-ci dsl validate reproducibility.yml --format json --output validation.json

# Normalize to canonical JSON
oss-paper-ci dsl normalize reproducibility.yml --format json --output canonical.json

# Generate DAG in DOT format
oss-paper-ci dsl graph reproducibility.yml --output dag.dot

# Render DAG to PNG (requires Graphviz)
dot -Tpng dag.dot -o dag.png

# Generate execution plan
oss-paper-ci dsl plan reproducibility.yml --format markdown --output plan.md

# Generate execution plan (JSON)
oss-paper-ci dsl plan reproducibility.yml --format json --output plan.json

# Generate execution plan (HTML)
oss-paper-ci dsl plan reproducibility.yml --format html --output plan.html

# Explain DAG structure
oss-paper-ci dsl explain reproducibility.yml --format markdown --output explain.md

# Migrate legacy config
oss-paper-ci dsl migrate old.yml --output new.yml

# Migrate with report
oss-paper-ci dsl migrate old.yml --format markdown --output migration-report.md
```

## Common patterns

### Linear pipeline

```
step-a --> step-b --> step-c --> step-d
```

Each step depends on the previous one.

### Fan-out

```
step-a --> step-b
       --> step-c
       --> step-d
```

Multiple steps depend on the same predecessor.

### Fan-in

```
step-a --> step-c
step-b --> step-c
```

A step depends on multiple predecessors.

### Diamond

```
step-a --> step-b --> step-d
step-a --> step-c --> step-d
```

Fan-out followed by fan-in.  Steps b and c can run in parallel.

## Related documentation

- [Reproducibility DSL Overview](reproducibility-dsl.md)
- [Reproducibility Schema v1](reproducibility-schema-v1.md)
- [DAG Planner](dag-planner.md)
- [DSL Safety](dsl-safety.md)
- [DSL Migration](dsl-migration.md)
- [DSL GitHub Actions](dsl-github-actions.md)
