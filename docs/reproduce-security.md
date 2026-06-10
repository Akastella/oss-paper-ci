# Reproduce Security

The `oss-paper-ci reproduce` command runs code from external repositories.
This document describes the security model and risks.

## Default Behavior (Safe)

By default, `reproduce` runs in **dry-run mode**:

- No code is executed
- No dependencies are installed
- No network requests (beyond git clone)
- No filesystem changes (beyond reading)

Only `--execute` enables code execution, and only `--install` enables
dependency installation. Both must be explicitly provided.

## What `--execute` Does

When `--execute` is provided:

1. Clones the repository to a temporary directory
2. Creates an isolated Python virtual environment
3. Installs dependencies from requirements.txt or pyproject.toml
4. Runs the detected or specified reproduction command
5. Captures stdout/stderr, exit code, and timing
6. Runs oss-paper-ci scan on the repository
7. Generates a report

## Risks

### Arbitrary Code Execution

`--execute` runs commands from the cloned repository. This is inherently
risky. Only use `--execute` on repositories you trust.

### Network Access

The cloned repository's scripts may make network requests. oss-paper-ci
does not sandbox network access.

### Filesystem Access

Scripts may read/write files in the working directory. oss-paper-ci uses
a temporary directory, but scripts could still access files outside it.

### Resource Consumption

Scripts may consume significant CPU, memory, or disk. The `--timeout`
flag limits per-command wall-clock time, but does not limit resource usage.

## Mitigations

- **Dangerous command detection**: known dangerous patterns (rm -rf /,
  sudo, fork bombs) are blocked before execution.
- **Timeout**: every command has a configurable timeout (default 300s).
- **Isolated workdir**: clone and execution happen in a temporary directory.
- **No auto-install**: dependencies are only installed with `--install`.
- **No auto-execution**: commands are only run with `--execute`.

## Recommendations

- **CI**: only use `--execute` on trusted repositories in CI pipelines.
- **Local**: review the reproduction report from `--dry-run` before
  deciding to use `--execute`.
- **Timeout**: use `--timeout` to limit long-running commands.
- **Workdir**: use `--keep-workdir` to inspect what was generated.

## What This Tool Does NOT Do

- Does not sandbox execution (no Docker, no chroot, no seccomp)
- Does not block network access
- Does not limit CPU/memory usage
- Does not verify scientific correctness
- Does not guarantee numerical reproducibility
