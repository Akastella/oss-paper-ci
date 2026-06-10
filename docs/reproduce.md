# One-Command Reproduction

The `oss-paper-ci reproduce` command attempts to clone, install, and run a
scientific paper repository, then generates a structured report of the attempt.

## Quick Start

```bash
# Dry-run: see what would happen (default, safe)
oss-paper-ci reproduce https://github.com/owner/paper-repo --dry-run

# Execute: actually run the reproduction
oss-paper-ci reproduce https://github.com/owner/paper-repo --execute --install

# Generate HTML report
oss-paper-ci reproduce https://github.com/owner/paper-repo \
  --execute --install --format html --output report.html
```

## Safety Model

The reproduce command is **safe by default**:

- **Default mode is dry-run**: no code is executed, no dependencies installed.
- **`--execute` is required** to actually run reproduction commands.
- **`--install` is required** to install dependencies into an isolated venv.
- Dangerous commands (rm -rf, sudo, fork bombs) are blocked.
- Every command has a configurable timeout (default: 300s).
- Work is done in an isolated temporary directory (not your current repo).

## Command Reference

```
oss-paper-ci reproduce URL [options]

Arguments:
  URL                   GitHub URL, local path, or paper URL

Options:
  --repo URL            Explicit repository URL (for paper URLs)
  --dry-run             Show what would happen (default)
  --execute             Actually run commands
  --install             Install dependencies into isolated venv
  --no-install          Skip dependency installation
  --command "..."       Override the reproduction command
  --workdir PATH        Use a specific working directory
  --keep-workdir        Preserve working directory after run
  --timeout N           Per-command timeout in seconds (default: 300)
  --format FORMAT       Output format: markdown, json, html
  --output FILE         Write report to file
```

## What It Does

1. **Resolves the source**: GitHub URL → clone, local path → use directly
2. **Detects environment**: requirements.txt, pyproject.toml, etc.
3. **Detects commands**: from reproducibility.yml or common script paths
4. **Installs** (if `--install`): creates venv, installs dependencies
5. **Runs commands** (if `--execute`): executes reproduction commands
6. **Scans**: runs oss-paper-ci scan on the repository
7. **Reports**: generates Markdown, JSON, or HTML report

## Supported Sources

- **GitHub URLs**: `https://github.com/owner/repo`
- **Local paths**: `./path/to/repo`, `/absolute/path`
- **file:// URIs**: `file:///path/to/repo`
- **Paper URLs**: arXiv, DOI — requires `--repo` to specify the code

## See Also

- [Reproduce Security](reproduce-security.md) — security model and risks
- [Environment Detection](environment-detection.md) — how environments are detected
- [Reproduction Report](reproduction-report.md) — report format details
