# Evaluation Corpus for oss-paper-ci

**WARNING: This is a synthetic test corpus. These are NOT real repositories.**

This directory contains 12 synthetic but realistic test repositories designed to evaluate the `oss-paper-ci` tool's scanning, scoring, and scaffolding capabilities. Each repository is a minimal fixture that simulates common patterns found in research software projects.

## Purpose

- Test ecosystem detection (Python, R, Julia, Node.js, Make, Snakemake, C++)
- Test reproducibility scoring accuracy
- Test risk detection (unsafe commands, eval patterns)
- Test scaffolding suggestion generation
- Test adoption workflow before/after comparisons

## Repositories

| ID | Description | Expected Status |
|----|-------------|-----------------|
| `python_good_repro` | Well-structured Python ML project | good |
| `python_missing_data` | Python project missing data documentation | needs-work |
| `python_missing_environment` | Python project missing environment files | needs-work |
| `python_bad_results` | Python project with invalid results JSON | critical |
| `r_repro_project` | R project with renv | good |
| `julia_project` | Julia project with Project.toml | good |
| `node_analysis_project` | Node.js analysis project | good |
| `make_workflow_project` | Make-based workflow | good |
| `snakemake_project` | Snakemake workflow | good |
| `cpp_build_project` | C++ project with CMake | needs-work |
| `unsafe_script_project` | Repo with risky commands (DO NOT EXECUTE) | critical |
| `adoption_before_after` | Before/after adoption comparison | varies |

## Important Notes

1. **No real computation**: All scripts contain only print statements or minimal logic.
2. **No real data**: Data directories contain only documentation files.
3. **No real dependencies**: Requirements files list packages but nothing needs installing.
4. **Safety**: The `unsafe_script_project` contains patterns like `curl | bash` and `eval()` purely as text fixtures for testing dry-run detection. These scripts are never executed by the test suite.

## Usage

```bash
# Run oss-paper-ci against a single test repo
oss-paper-ci scan examples/evaluation-corpus/python_good_repro

# Run against the entire corpus
oss-paper-ci scan examples/evaluation-corpus/
```

## Schema

See `expected_outcomes.yml` for the expected scan results for each repository.
