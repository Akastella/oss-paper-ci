# Smoke Runs

The `smoke` command executes a lightweight experiment command inside a
sandboxed runner.  It is designed to verify that the setup works before
committing to a full experiment run.

## Quick start

```bash
# Run the default "smoke" experiment from reproducibility.yml
oss-paper-ci smoke .

# Run a specific experiment by ID
oss-paper-ci smoke . --experiment quick_check

# Provide an explicit command
oss-paper-ci smoke . --command "python scripts/train.py --epochs 1"

# Preview without executing
oss-paper-ci smoke . --command "python train.py" --dry-run
```

## Command reference

```bash
oss-paper-ci smoke [PATH] [OPTIONS]
```

| Option             | Description                                           |
|--------------------|-------------------------------------------------------|
| `PATH`             | Repository root (default: `.`)                        |
| `--contract FILE`  | Path to `reproducibility.yml` (auto-detected if omitted) |
| `--experiment ID`  | Experiment ID to run (default: `smoke`)               |
| `--command CMD`    | Override the command instead of reading from contract |
| `--timeout SECS`   | Max wall-clock seconds (default: 60)                  |
| `--dry-run`        | Print the command without executing it                |
| `--format FORMAT`  | `text` (default) or `json`                            |

## Contract file

If you don't pass `--command`, the runner reads from a `reproducibility.yml`
(or `.yaml`) file in the repo root.  The expected structure is:

```yaml
experiments:
  smoke:
    command: "python scripts/train.py --quick"
    description: "Fast sanity check"
  full:
    command: "python scripts/train.py --epochs 100"
    description: "Full training run"
```

The `experiments.<id>.command` field is the shell command that will be
executed.

## Safety model

The smoke runner is **safe by default**:

1. **Dangerous-command blocklist** -- Commands matching known destructive
   patterns (e.g. `rm -rf /`, `sudo`, `curl | sh`, `mkfs`, `dd if=`)
   are blocked before execution.

2. **Timeout** -- Every command has a hard wall-clock timeout (default 60s).
   If the command doesn't finish in time, it is killed and the result is
   recorded as timed-out.

3. **Working directory** -- The command always runs with the repo root as its
   working directory.

4. **No automatic invocation** -- `oss-paper-ci smoke` must be called
   explicitly.  The `scan` command never runs smoke tests.

5. **Output capture** -- stdout and stderr are captured and truncated
   (max ~2000 characters each) to prevent context overflow.

6. **Structured results** -- Every run produces a `SmokeResult` with exit
   code, duration, timeout flag, and output excerpts.  In JSON mode this
   is machine-parseable for CI pipelines.

## Expected outputs

When called programmatically, `run_smoke()` accepts an
`expected_outputs` parameter listing file paths that should exist after
the command completes.  The result includes a per-file pass/fail:

```json
{
  "expected_outputs": [
    {"path": "results/metrics.json", "exists": true},
    {"path": "results/figure.png", "exists": false}
  ]
}
```

## CI integration

```yaml
- name: Smoke test
  run: |
    oss-paper-ci smoke . --experiment smoke --timeout 120 --format json
```

Exit codes:
- **0** -- command ran and succeeded (exit code 0, no timeout, not blocked).
- **1** -- command failed, timed out, or was blocked.
- **2** -- configuration error (missing contract, bad path, etc.).

## JSON output schema

When `--format json` is used, the output is a single JSON object:

```json
{
  "experiment_id": "smoke",
  "command": "python scripts/train.py --quick",
  "exit_code": 0,
  "duration_seconds": 3.214,
  "timed_out": false,
  "blocked": false,
  "block_reason": "",
  "expected_outputs": [],
  "stdout_excerpt": "Training complete.\n",
  "stderr_excerpt": ""
}
```
