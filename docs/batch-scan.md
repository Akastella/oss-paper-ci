# Batch Scanning

Batch scanning runs oss-paper-ci across all projects defined in a workspace.

## Basic Usage

```bash
oss-paper-ci batch scan --workspace oss-paper-ci-workspace.yml
```

## Output Formats

```bash
# Markdown (default)
oss-paper-ci batch scan --workspace oss-paper-ci-workspace.yml --format markdown

# JSON
oss-paper-ci batch scan --workspace oss-paper-ci-workspace.yml --format json --output batch-report.json

# HTML (single file, no external CDN)
oss-paper-ci batch scan --workspace oss-paper-ci-workspace.yml --format html --output batch-report.html
```

## Error Isolation

Each project is scanned independently. If one project fails (e.g., path does not exist,
scan crashes), the error is recorded in the batch report and scanning continues with
the remaining projects.

## Batch Report Structure

### JSON

```json
{
  "schema_version": "0.5",
  "tool": "oss-paper-ci",
  "version": "1.7.0rc1",
  "workspace": {
    "name": "my-workspace",
    "project_count": 3
  },
  "summary": {
    "pass": 2,
    "warn": 1,
    "fail": 0,
    "error": 0,
    "average_score": 88.3
  },
  "projects": [
    {
      "id": "project-a",
      "path": "./project-a",
      "profile": "publication",
      "status": "pass",
      "score": 93,
      "finding_counts": {
        "blocking": 0,
        "important": 1,
        "advisory": 3
      },
      "cache_hit": false
    }
  ],
  "cache": {
    "total": 3,
    "hits": 0,
    "misses": 3,
    "errors": 0
  }
}
```

### Markdown

The Markdown report includes:
- Workspace summary
- Project table with scores and finding counts
- Failed/error project details
- Cache summary
- Footer with tool version

### HTML

Single-file HTML report with:
- No external CDN dependencies
- Summary cards
- Project table with status badges
- All user text HTML-escaped

## Exit Codes

| Code | Meaning |
|------|---------|
| 0 | All projects passed |
| 1 | Some projects have warnings |
| 2 | Some projects failed or errored |

Projects with `allow_failure: true` still contribute findings but their
fail/errors are not counted toward the batch exit code.

## Notes

- Batch report is an engineering governance tool, not a scientific quality assessor
- Output order matches workspace project order
