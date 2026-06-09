# Parallel Execution

Batch scanning supports parallel execution via `--jobs N`.

## Usage

```bash
# Sequential (default)
oss-paper-ci batch scan --workspace oss-paper-ci-workspace.yml

# Parallel with 2 workers
oss-paper-ci batch scan --workspace oss-paper-ci-workspace.yml --jobs 2

# Parallel with 4 workers
oss-paper-ci batch scan --workspace oss-paper-ci-workspace.yml --jobs 4
```

## Behavior

- `--jobs 1` (default): Sequential execution, one project at a time
- `--jobs N` (N > 1): Up to N projects scanned concurrently
- `--jobs 0` or negative: Error

## Implementation

Uses Python `concurrent.futures.ProcessPoolExecutor` for true parallelism.
Works on both Windows and Linux (no fork-only dependency).

## Output Order

Regardless of `--jobs`, the output order always matches the workspace
project order. Results are collected and sorted before output.

## Determinism

Parallel execution does not change scan results. Each project is scanned
independently with its own config. The only difference is wall-clock time.

## Notes

- Parallelism does not sacrifice reproducibility
- Cache works correctly with parallel execution
- Single project errors are isolated and do not crash the batch
