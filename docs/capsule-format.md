# Capsule Format

## Schema Version

Current schema version: `0.1`

The schema version is stored in `capsule.json` as `schema_version`.
Future versions may add fields but will not remove existing ones.

## capsule.json

The manifest file at the root of the capsule.

```json
{
  "schema_version": "0.1",
  "capsule_type": "oss-paper-ci-reproduction-capsule",
  "created_by": "oss-paper-ci",
  "oss_paper_ci_version": "1.9.0rc1",
  "source": {
    "input_url": "...",
    "repo_url": "...",
    "paper_url": null,
    "commit_sha": "...",
    "source_type": "github|local|paper-with-repo"
  },
  "execution": {
    "mode": "dry-run|execute",
    "install": true,
    "commands_attempted": 3,
    "commands_succeeded": 3,
    "commands_failed": 0,
    "timeout_seconds": 300
  },
  "reports": {
    "reproduce_json": "reports/reproduce_report.json",
    "reproduce_html": "reports/reproduce_report.html",
    "scan_json": "reports/scan_report.json"
  },
  "integrity": {
    "sha256sums": "SHA256SUMS"
  },
  "limitations": [
    "This capsule records a reproduction attempt, not a proof of paper correctness."
  ]
}
```

## SHA256SUMS

Each line contains a SHA256 hash and a relative path:

```
<sha256hex>  capsule.json
<sha256hex>  reports/reproduce_report.json
...
```

The SHA256SUMS file itself is not hashed (it covers all other files).

## Path Rules

- All paths are relative to the capsule root (`oss-paper-ci-capsule/`)
- No absolute paths are stored (redacted to `<redacted>/basename`)
- No path traversal (`..`) is allowed
- No symlinks are followed

## Size Limits

- Max artifact file size: 10 MB (configurable)
- Max total capsule size: 100 MB
- Max artifact file count: 200
- Max log file size: 1 MB (truncated if larger)

## Excluded Patterns

These are never packaged into a capsule:

- `.git/`, `__pycache__/`, `*.pyc`
- `venv/`, `.venv/`, `node_modules/`
- `.oss-paper-ci-repro/`, `.oss-paper-ci-cache/`
