# Workspace Examples

This directory contains example workspace configurations for batch scanning
multiple projects with oss-paper-ci.

## Available Workspaces

| File | Description |
|------|-------------|
| `demo-workspace.yml` | 3 projects with mixed profiles, one with `allow_failure` |
| `strict-publication-workspace.yml` | 3 projects all using `publication` profile |
| `mixed-fixtures-workspace.yml` | 8 fixture repos with various profiles |

## Usage

```bash
# Validate a workspace
oss-paper-ci workspace validate --workspace examples/workspaces/demo-workspace.yml

# List projects
oss-paper-ci workspace list --workspace examples/workspaces/demo-workspace.yml

# Batch scan
oss-paper-ci batch scan --workspace examples/workspaces/demo-workspace.yml --format markdown

# Batch scan with parallel jobs and cache
oss-paper-ci batch scan --workspace examples/workspaces/demo-workspace.yml --jobs 2 --cache --format json --output batch-report.json
```

## Notes

- Workspace paths are relative to the workspace file location.
- Each project can override `profile`, `config`, `rules`, and `fail_under`.
- `allow_failure` affects batch exit code but does not hide findings.
- This is a local batch scanning tool, not a cloud project management system.
