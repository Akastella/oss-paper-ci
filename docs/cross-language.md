# Cross-Language Support

oss-paper-ci provides basic reproducibility checks for multiple research languages.

## Supported Languages

### Python (Full Support)
- Environment files (requirements.txt, pyproject.toml)
- Entry points (argparse, click, typer)
- Seed setting detection
- Config file detection
- Result/figure output detection

### R (Basic Support)
Detection:
- `DESCRIPTION` file
- `renv.lock` for dependency management
- `.R` scripts in `scripts/`
- `.Rproj` files

Checks:
- Environment specification (renv.lock)
- Script entry points
- Seed setting (`set.seed`)

### Julia (Basic Support)
Detection:
- `Project.toml` for dependencies
- `Manifest.toml` for lock file
- `.jl` scripts in `scripts/`

Checks:
- Environment specification
- Script entry points

### MATLAB (Basic Support)
Detection:
- `.m` files
- `startup.m` for path setup

Checks:
- Script entry points
- Version/toolbox documentation

### Make/Snakemake (Basic Support)
Detection:
- `Makefile` for build targets
- `Snakefile` for workflow rules

Checks:
- Target definitions
- Smoke/test targets
- Reproduce targets

## Limitations

Cross-language support is basic detection and simple checks. It does not:
- Parse R/Julia/MATLAB ASTs
- Verify dependency compatibility
- Execute cross-language scripts
- Validate container configurations

## Fixtures

Test fixtures for each language are in `tests/fixtures/`:
- `r_ready_repo/` — R project with renv, scripts, data
- `julia_ready_repo/` — Julia project with Project.toml, scripts
- `matlab_minimal_repo/` — MATLAB project with scripts, startup.m
- `make_snakemake_repo/` — Make/Snakemake project with targets
