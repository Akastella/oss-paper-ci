# Doctor Command

The `doctor` command diagnoses your repository and environment to identify
common issues before running a full scan.

## Usage

```bash
oss-paper-ci doctor .
oss-paper-ci doctor . --format json
oss-paper-ci doctor . --format markdown
```

## What it checks

1. Python version compatibility
2. oss-paper-ci installation
3. README.md presence
4. LICENSE presence
5. Environment file (requirements.txt, pyproject.toml, etc.)
6. reproducibility.yml contract
7. GitHub Actions workflows
8. Common directories (results/, figures/, data/, scripts/)

## Output

The command reports each check as `ok` or `missing`, and suggests next steps.

```
  [ok] Python version: 3.12.0
  [ok] oss-paper-ci version: 1.3.0rc1
  [ok] README.md: /path/to/repo/README.md
  [ok] LICENSE: /path/to/repo/LICENSE
  [ok] Environment file: requirements.txt
  [MISSING] reproducibility.yml: /path/to/repo/reproducibility.yml
  [ok] GitHub workflows: /path/to/repo/.github/workflows
  [MISSING] results/: /path/to/repo/results
  [MISSING] figures/: /path/to/repo/figures
  [MISSING] data/: /path/to/repo/data
  [ok] scripts/: /path/to/repo/scripts

Suggested next steps:
  - Run `oss-paper-ci init --contract` to create reproducibility.yml
```

## Limitations

- Doctor does not execute any scripts or tests
- Doctor does not check network connectivity
- Doctor does not validate file contents, only existence
- Doctor is not a security audit

## Next steps after doctor

If doctor reports issues:

1. Run `oss-paper-ci init --all` to scaffold missing files
2. Run `oss-paper-ci scan .` for a full analysis
3. Fix blocking issues reported by the scan
