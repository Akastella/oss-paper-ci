# Reproducibility Contract

A **reproducibility contract** is an optional YAML file (`reproducibility.yml`) that explicitly describes how to reproduce the computational results of a scientific paper.  It tells `oss-paper-ci` (and anyone cloning your repository) exactly which data, code, experiments, and outputs are involved.

## Why use a contract?

Without a contract, `oss-paper-ci` uses **inferred mode** -- it scans the repository and guesses which files are paper-related.  This works reasonably well, but a contract gives you:

- **Precision** -- you define exactly which experiments produce which figures and results.
- **Validation** -- `oss-paper-ci` can check that referenced files, scripts, and datasets actually exist.
- **CI integration** -- the contract can specify a smoke experiment to run in CI and a minimum score threshold.
- **Documentation** -- the contract serves as a machine-readable description of your computational workflow.

The contract is entirely optional.  If no `reproducibility.yml` is found, all checks still run in inferred mode.

## Quick start

Generate a contract template:

```bash
oss-paper-ci init --contract
```

This creates a `reproducibility.yml` in the current directory.  Edit it to match your project.

You can choose a template style:

```bash
oss-paper-ci init --contract --template ml              # Machine learning
oss-paper-ci init --contract --template simulation       # Simulation / HPC
oss-paper-ci init --contract --template data-science     # Data analysis
oss-paper-ci init --contract --template default          # Generic
```

Validate an existing contract:

```bash
oss-paper-ci validate-contract .
```

## Schema reference

The contract has the following top-level fields:

| Field | Type | Description |
|-------|------|-------------|
| `version` | string | Schema version (currently `"0.3"`) |
| `project_name` | string | Human-readable project name |
| `project_type` | string | One of: `ml`, `simulation`, `data-science`, `analysis`, `other` |
| `paper` | object | Paper location |
| `environment` | object | Environment specification |
| `data` | list | Dataset descriptions |
| `experiments` | list | Experiment definitions |
| `figures` | list | Figure descriptions |
| `results` | list | Result file descriptions |
| `ci` | object | CI integration settings |

### `paper`

| Field | Type | Description |
|-------|------|-------------|
| `path` | string | Path to the paper file (LaTeX source or PDF) |
| `bibliography` | list[string] | Paths to bibliography files |

### `environment`

| Field | Type | Description |
|-------|------|-------------|
| `type` | string | Environment type: `python`, `conda`, `docker`, `r`, `julia`, `other` |
| `file` | string | Path to the environment file (e.g., `requirements.txt`, `environment.yml`) |
| `python` | string | Python version (informational) |
| `containers` | list[dict] | Container definitions (optional) |

### `data` (list)

Each entry:

| Field | Type | Description |
|-------|------|-------------|
| `id` | string | Unique identifier |
| `path` | string | Path to the data in the repository |
| `availability` | string | `public`, `private`, `synthetic`, `external`, or `not-required` |
| `source` | string | URL or citation for obtaining the data |
| `license` | string | Data license |
| `preprocessing` | dict | Preprocessing script and outputs (optional) |

**Validation behavior**: Paths with `availability: external` or `availability: not-required` are not checked -- they are expected to be absent from the repository.

### `experiments` (list)

Each entry:

| Field | Type | Description |
|-------|------|-------------|
| `id` | string | Unique identifier |
| `description` | string | What the experiment does |
| `command` | string | Shell command to run |
| `timeout_seconds` | int | Maximum runtime (default: 60) |
| `safe_to_run` | bool | Whether it is safe to run in CI |
| `expected_outputs` | list[string] | Files produced by the experiment |

**Validation behavior**: If the command references a script file (e.g., `python scripts/train.py`), the checker verifies the script exists.

### `figures` (list)

Each entry:

| Field | Type | Description |
|-------|------|-------------|
| `id` | string | Unique identifier |
| `path` | string | Output path of the figure |
| `generated_by` | list[string] | Experiment IDs that produce this figure |
| `referenced_by` | list[string] | Paper sections that reference this figure |

### `results` (list)

Each entry:

| Field | Type | Description |
|-------|------|-------------|
| `id` | string | Unique identifier |
| `path` | string | Path to the result file |
| `generated_by` | list[string] | Experiment IDs that produce this result |

### `ci`

| Field | Type | Description |
|-------|------|-------------|
| `smoke_experiment` | string | Experiment ID to run as a CI smoke test |
| `min_score` | int | Minimum reproducibility score to pass CI |
| `fail_on_regression` | bool | Fail CI if score drops below a saved baseline |

## Validation

Run validation from the command line:

```bash
oss-paper-ci validate-contract /path/to/repo
```

Or point to a specific contract file:

```bash
oss-paper-ci validate-contract /path/to/repo --contract path/to/reproducibility.yml
```

Validation checks:

1. **Paper path** exists in the repository.
2. **Bibliography files** exist.
3. **Environment file** (e.g., `requirements.txt`) exists.
4. **Data paths** exist (unless `availability` is `external` or `not-required`).
5. **Experiment commands** reference scripts that exist.
6. **Figure and result directories** exist (outputs may not exist yet -- only directories are checked).

## Integration with scan

When you run `oss-paper-ci scan`, the `CONTRACT001` check automatically:

1. Searches for `reproducibility.yml` in the repository root.
2. If found, parses and validates it, reporting any issues.
3. If not found, reports an informational message suggesting you create one.

The contract check does not block the scan -- it is an `INFO`-severity check by default.  Validation issues raised by the contract are reported as `WARNING` level.

## Example

See [`examples/reproducibility.yml`](../examples/reproducibility.yml) for a fully commented example contract for a machine learning project.
