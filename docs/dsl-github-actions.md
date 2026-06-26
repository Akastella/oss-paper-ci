# DSL GitHub Actions Integration

This document shows how to integrate DSL validation and planning into GitHub
Actions workflows.  All examples are read-only; no code is executed, no packages
are installed, and no network access is performed beyond what the workflow itself
requires.

## Basic validation

Validate the DSL file on every push and pull request:

```yaml
name: DSL Validate

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

permissions:
  contents: read

jobs:
  validate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - uses: actions/setup-python@v5
        with:
          python-version: "3.10"

      - name: Install oss-paper-ci
        run: pip install -e ".[dev]"

      - name: Validate DSL
        run: |
          oss-paper-ci dsl validate reproducibility.yml \
            --format markdown \
            --output validation-report.md

      - name: Upload validation report
        uses: actions/upload-artifact@v4
        with:
          name: validation-report
          path: validation-report.md

      - name: Summary
        if: always()
        run: |
          echo "## DSL Validation" >> $GITHUB_STEP_SUMMARY
          echo "" >> $GITHUB_STEP_SUMMARY
          cat validation-report.md >> $GITHUB_STEP_SUMMARY
```

## Validation with DAG visualization

Generate the dependency graph alongside validation:

```yaml
name: DSL Validate + DAG

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

permissions:
  contents: read

jobs:
  validate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - uses: actions/setup-python@v5
        with:
          python-version: "3.10"

      - name: Install oss-paper-ci
        run: pip install -e ".[dev]"

      - name: Validate DSL
        run: |
          oss-paper-ci dsl validate reproducibility.yml \
            --format json \
            --output validation.json

      - name: Generate dependency graph
        run: |
          oss-paper-ci dsl graph reproducibility.yml \
            --output dag.dot

      - name: Generate execution plan
        run: |
          oss-paper-ci dsl plan reproducibility.yml \
            --format markdown \
            --output plan.md

      - name: Explain DAG
        run: |
          oss-paper-ci dsl explain reproducibility.yml \
            --format markdown \
            --output dag-explain.md

      - name: Upload artifacts
        uses: actions/upload-artifact@v4
        with:
          name: dsl-validation
          path: |
            validation.json
            dag.dot
            plan.md
            dag-explain.md

      - name: Summary
        if: always()
        run: |
          echo "## DSL Validation" >> $GITHUB_STEP_SUMMARY
          echo "" >> $GITHUB_STEP_SUMMARY
          cat plan.md >> $GITHUB_STEP_SUMMARY
```

## Dry-run reproduction

Generate an execution plan and run a dry-run reproduction without executing
any code:

```yaml
name: DSL Reproduce (Dry Run)

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

permissions:
  contents: read

jobs:
  reproduce-dry-run:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - uses: actions/setup-python@v5
        with:
          python-version: "3.10"

      - name: Install oss-paper-ci
        run: pip install -e ".[dev]"

      - name: Validate DSL
        run: |
          oss-paper-ci dsl validate reproducibility.yml \
            --format json \
            --output validation.json

      - name: Generate execution plan
        run: |
          oss-paper-ci dsl plan reproducibility.yml \
            --format json \
            --output plan.json

      - name: Generate execution plan (markdown)
        run: |
          oss-paper-ci dsl plan reproducibility.yml \
            --format markdown \
            --output plan.md

      - name: Run reproduce dry-run
        run: |
          oss-paper-ci reproduce . \
            --dry-run \
            --format markdown \
            --output reproduce-report.md

      - name: Upload dry-run artifacts
        uses: actions/upload-artifact@v4
        with:
          name: dsl-dry-run
          path: |
            validation.json
            plan.json
            plan.md
            reproduce-report.md

      - name: Summary
        if: always()
        run: |
          echo "## Reproduction Dry-Run" >> $GITHUB_STEP_SUMMARY
          echo "" >> $GITHUB_STEP_SUMMARY
          cat plan.md >> $GITHUB_STEP_SUMMARY
```

## Matrix testing

Run DSL validation across multiple Python versions:

```yaml
name: DSL Matrix

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

permissions:
  contents: read

jobs:
  matrix:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: ["3.10", "3.11", "3.12"]
      fail-fast: false

    steps:
      - uses: actions/checkout@v4

      - name: Set up Python ${{ matrix.python-version }}
        uses: actions/setup-python@v5
        with:
          python-version: ${{ matrix.python-version }}

      - name: Install oss-paper-ci
        run: pip install -e ".[dev]"

      - name: Validate DSL
        run: |
          oss-paper-ci dsl validate reproducibility.yml \
            --format json \
            --output validation-py${{ matrix.python-version }}.json

      - name: Generate execution plan
        run: |
          oss-paper-ci dsl plan reproducibility.yml \
            --format json \
            --output plan-py${{ matrix.python-version }}.json

      - name: Upload matrix variant artifacts
        uses: actions/upload-artifact@v4
        with:
          name: dsl-matrix-py${{ matrix.python-version }}
          path: |
            validation-py${{ matrix.python-version }}.json
            plan-py${{ matrix.python-version }}.json

      - name: Summary
        if: always()
        run: |
          echo "## DSL Matrix -- Python ${{ matrix.python-version }}" >> $GITHUB_STEP_SUMMARY
          echo "" >> $GITHUB_STEP_SUMMARY
          cat validation-py${{ matrix.python-version }}.json >> $GITHUB_STEP_SUMMARY
```

## Session-based workflow

Start a reproduction session from a DSL file and generate reports:

```yaml
name: DSL Session

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

permissions:
  contents: read

jobs:
  session:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - uses: actions/setup-python@v5
        with:
          python-version: "3.10"

      - name: Install oss-paper-ci
        run: pip install -e ".[dev]"

      - name: Validate DSL before session
        run: |
          oss-paper-ci dsl validate reproducibility.yml \
            --format json \
            --output pre-session-validation.json

      - name: Start reproduction session (dry-run)
        run: |
          oss-paper-ci session start . \
            --name ci-dsl-session \
            --output-dir .oss-paper-ci-sessions/ci-dsl-session

      - name: Generate session report (markdown)
        run: |
          oss-paper-ci session report .oss-paper-ci-sessions/ci-dsl-session \
            --format markdown \
            --output session-report.md

      - name: Create evidence bundle
        run: |
          oss-paper-ci session bundle .oss-paper-ci-sessions/ci-dsl-session \
            --output session-evidence.zip

      - name: Upload session artifacts
        uses: actions/upload-artifact@v4
        with:
          name: dsl-session
          path: |
            pre-session-validation.json
            session-report.md
            session-evidence.zip

      - name: Summary
        if: always()
        run: |
          echo "## DSL Session Report" >> $GITHUB_STEP_SUMMARY
          echo "" >> $GITHUB_STEP_SUMMARY
          cat session-report.md >> $GITHUB_STEP_SUMMARY
```

## Migration workflow

Migrate legacy configs as part of CI:

```yaml
name: DSL Migration Check

on:
  pull_request:
    branches: [main]

permissions:
  contents: read

jobs:
  migration:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - uses: actions/setup-python@v5
        with:
          python-version: "3.10"

      - name: Install oss-paper-ci
        run: pip install -e ".[dev]"

      - name: Check if migration is needed
        run: |
          oss-paper-ci dsl validate reproducibility.yml \
            --format json \
            --output validation.json

      - name: Generate migration report (if legacy)
        run: |
          oss-paper-ci dsl migrate reproducibility.yml \
            --format markdown \
            --output migration-report.md || true

      - name: Upload artifacts
        uses: actions/upload-artifact@v4
        with:
          name: migration-check
          path: |
            validation.json
            migration-report.md
```

## Output formats

All DSL commands support these output formats:

| Format     | Commands                                  |
|------------|-------------------------------------------|
| `markdown` | validate, plan, explain, migrate          |
| `json`     | validate, normalize, plan, explain, migrate |
| `html`     | plan, explain                             |
| `dot`      | graph (default, not configurable)         |

Use `--format` to select the format and `--output` to write to a file.

## Behavior notes

- All DSL commands default to dry-run mode.  No code is executed.
- The tool never auto-executes, auto-installs, or auto-fixes code.
- Validation returns exit code 0 on success, 2 on errors.
- Plan returns exit code 0 if executable, 1 if not.
- Legacy files (v0.2/v0.3) are automatically detected and converted.
- All output is deterministic and can be diffed across runs.

## Related documentation

- [Reproducibility DSL Overview](reproducibility-dsl.md)
- [Reproducibility Schema v1](reproducibility-schema-v1.md)
- [DAG Planner](dag-planner.md)
- [DSL Safety](dsl-safety.md)
- [DSL Examples](dsl-examples.md)
- [DSL Migration](dsl-migration.md)
