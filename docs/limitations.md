# Limitations

oss-paper-ci is a static analysis tool. It has real constraints that users
should understand before relying on its output.

## What it cannot do

### No deep LaTeX compilation

The tool can detect `.tex` files and check for `\includegraphics` paths, but
it does not compile LaTeX. It cannot verify that a document builds, that
cross-references resolve, or that bibliographies are complete.

### No experiment execution

oss-paper-ci does not run any code. It cannot verify that `train.py` actually
trains a model, that `run.sh` completes without errors, or that the results
match the paper.

### No result value verification

The tool checks whether results directories exist and whether figure-generation
scripts are present. It does not compare output numbers against reported metrics
in the paper.

### Static analysis only

All checks are file-system scans and text pattern matching. There is no AST
parsing, no import resolution, no dependency graph analysis. The tool checks
whether files exist and contain expected patterns, not whether the code is
correct.

### Cross-language depth varies

Python has the deepest static analysis: environment files, entry points, seed
setting, config detection, and result output detection. R, Julia, MATLAB, Make,
and Snakemake currently receive basic reproducibility asset checks (environment
files, script entry points, data/result directories), not full semantic
validation. See [cross-language.md](cross-language.md) for details. Go, Rust,
and other languages are not specifically handled.

### No container verification

The tool checks whether a `Dockerfile` or `Singularity` file exists. It does
not verify that the container builds, that the base image is correct, or that
all dependencies are installed inside it.

### Score is readiness, not quality

A score of 90/100 means the repository has most engineering basics in place.
It does not mean the research is good, the code is correct, or the results
are reliable. Conversely, a score of 30/100 does not mean the research is
bad -- it means the repository is missing common engineering practices.

### No version pinning analysis

The tool checks whether a lock file or pinned requirements exist. It does not
verify that the pinned versions are correct, up-to-date, or compatible with
each other.

### No notebook execution

Jupyter notebooks (`.ipynb`) are detected for project type classification,
but the tool does not execute notebooks or check for stale outputs.

## Known false-positive scenarios

- **Monorepos.** If a repo contains multiple papers or projects, the tool
  scans the entire tree. A `requirements.txt` in one subdirectory may satisfy
  an ENV check even if the paper being evaluated uses different dependencies.
- **Generated files.** If a results directory contains generated outputs
  committed to the repo, RES004 may flag them as orphan figures even if they
  are intentionally tracked.
- **Non-standard layouts.** Repos that use unusual directory structures may
  get lower scores even if they are well-organized for their domain.
- **Template repos.** Starter templates that include example READMEs, LICENSE
  files, and CI configs may score high even though the actual research content
  is minimal.
- **Multilingual repos.** Projects mixing Python with R, Julia, or other
  languages may get incomplete environment analysis for non-Python components.

## Known false-negative scenarios

- **Placeholder files.** An empty `README.md` or a `requirements.txt` with
  no actual dependencies will pass the corresponding checks.
- **Stale configs.** A `pyproject.toml` with outdated dependencies will pass
  ENV001 even though the environment is not reproducible.
- **Commented-out code.** Checks searching for patterns (e.g., seed setting)
  may match commented-out code.

## Intentional omissions

- No ML-based analysis. Deterministic checks are auditable and predictable.
- No network calls. The tool works offline and does not phone home.
- No subjective judgment. The tool evaluates file presence and patterns, not
  research quality.
- No license validation. The tool checks for a LICENSE file's existence, not
  whether it is a valid or appropriate license for the project.
