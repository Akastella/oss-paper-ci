# Security Model

## Default behavior (safe)

By default, oss-paper-ci operates in **scan mode**: it reads files and
produces reports. No code is executed, no dependencies are installed,
no network requests are made (beyond reading local files).

## Reproduction safety

The `reproduce` command has three safety levels:

1. **dry-run** (default): shows what would happen, executes nothing
2. **--install**: creates isolated venv, installs dependencies
3. **--execute**: runs reproduction commands from the repository

Only `--execute` enables code execution. Without it, the command only
reads and reports.

## What --execute does

When `--execute` is provided:

- Clones the repository to a temporary directory
- Creates an isolated Python virtual environment (with `--install`)
- Installs dependencies from requirements.txt or pyproject.toml
- Runs the detected or specified reproduction command
- Captures stdout/stderr, exit code, and timing
- Runs oss-paper-ci scan on the repository

## Dangerous command detection

Commands matching these patterns are blocked:

- `rm -rf /`, `rm -rf /*`
- `sudo`, `shutdown`, `mkfs`
- `curl | sh`, `wget | bash`
- Fork bombs, dd to devices

## Capsule safety

Capsules are evidence packages, not execution environments:

- SHA256 integrity verification
- Path traversal detection
- Absolute path redaction
- No symlinks followed
- venv/.git/cache excluded

## Recommendations

- Only use `--execute` on trusted repositories
- Review `--dry-run` output before executing
- Use `--timeout` to limit long-running commands
- Share capsules only after reviewing logs for sensitive information

## See also

- [Reproduce Security](reproduce-security.md) — detailed reproduce security
- [Capsule Security](capsule-security.md) — detailed capsule security
