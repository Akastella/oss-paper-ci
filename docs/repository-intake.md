# Repository Intake

Repository intake analyzes a repository and produces a structured report of its contents, ecosystems, commands, and artifacts. It is a **read-only** operation that does not execute any commands or modify the repository.

## Usage

```bash
# Analyze current directory
oss-paper-ci intake .

# Analyze a specific path
oss-paper-ci intake /path/to/repo

# Output as JSON
oss-paper-ci intake . --format json

# Output as HTML
oss-paper-ci intake . --format html

# Write to file
oss-paper-ci intake . --output intake-report.md
```

## What It Detects

### Languages & Ecosystems

Intake detects 14 language ecosystems: Python, R, Julia, MATLAB/Octave, Node.js, Rust, Java, C/C++, Make, Snakemake, Nextflow, and Shell scripts.

### Environment Files

- `requirements.txt`, `pyproject.toml`, `setup.py`, `setup.cfg`
- `environment.yml`, `conda.yml`, `Pipfile`
- `renv.lock`, `DESCRIPTION` (R)
- `Project.toml`, `Manifest.toml` (Julia)
- `package.json`, `package-lock.json`, `yarn.lock`
- `Cargo.toml`, `Cargo.lock` (Rust)
- `pom.xml`, `build.gradle` (Java)
- `CMakeLists.txt` (C/C++)
- `Dockerfile`, `docker-compose.yml`

### Commands

Commands are extracted from:
- **README/docs**: Fenced code blocks (```bash, ```sh) and inline commands
- **Makefile**: Targets (excluding `clean`, `help`)
- **Snakefile**: Rules
- **package.json**: Scripts section
- **pyproject.toml**: Scripts section
- **Shell scripts**: Files in `scripts/` directory

### Notebooks

Jupyter notebooks (`.ipynb`) are detected but not executed.

### Data & Result Paths

Common directory names are detected:
- Data: `data/`, `dataset/`, `input/`, `raw/`
- Results: `results/`, `output/`, `figures/`, `plots/`, `tables/`

## Confidence Scores

Intake produces confidence scores for:
- **Environment**: How well the environment can be detected
- **Commands**: How confident the extracted commands are
- **Artifacts**: How many artifacts were found
- **Metrics**: Whether metrics files exist
- **Overall**: Weighted average of the above

Scores range from 0.0 to 1.0. Higher scores indicate better detection quality, **not** scientific correctness.

## GitHub URLs

```bash
# This only parses the URL, does NOT clone
oss-paper-ci intake https://github.com/owner/repo

# This clones and analyzes
oss-paper-ci intake https://github.com/owner/repo --clone
```

When a GitHub URL is provided without `--clone`, intake produces a warning. With `--clone`, it performs a shallow clone (depth=1, no submodules, with timeout).

## Paper URLs

```bash
oss-paper-ci intake https://arxiv.org/abs/2401.00001
oss-paper-ci intake https://doi.org/10.1234/example
```

Paper URLs are recognized but **not fetched**. Intake produces a warning that a repository path is needed for analysis.

## Safety

- Intake is **read-only**: it never modifies the repository
- Intake **never executes** inferred commands
- Intake **never installs** dependencies
- Intake **never downloads** data
- Dangerous commands are **flagged** but not executed
- GitHub URLs require explicit `--clone`
- Paper URLs are recognized but not fetched

## Limitations

- Command candidates are inferred from documentation and config files
- Confidence scores indicate detection quality, not correctness
- Not all detected commands may be needed for reproduction
- Command ordering may not reflect actual dependency requirements
- Environment detection is based on file presence, not content analysis
- Paper URLs alone are not enough to reproduce; provide a repository path

## See Also

- [Autoplan](autoplan.md) -- Generate candidate reproducibility plan from intake
- [Reproduction Orchestrator](reproduction-orchestrator.md) -- Execute reproduction plans
- [Intake Safety](intake-safety.md) -- Detailed safety model
