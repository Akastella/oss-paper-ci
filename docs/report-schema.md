# JSON Report Schema

The JSON report produced by `oss-paper-ci scan --format json` follows this schema.

## Top-level fields

| Field            | Type   | Description                                     |
|------------------|--------|-------------------------------------------------|
| `schema_version`   | string | Schema version (currently `"0.2"`)              |
| `tool`             | string | Tool name (`"oss-paper-ci"`)                    |
| `version`          | string | Tool version (e.g., `"0.2.0"`)                 |
| `repository`       | object | Information about the scanned repository        |
| `summary`          | object | Aggregate results                               |
| `checks`           | array  | Individual check results                        |
| `metadata`         | object | Scan metadata (generated_at, scanned_files)     |
| `recommendations`  | array  | Top-level recommendations                       |
| `blocking_issues`  | array  | Issues that block pass status                   |

## `repository` object

| Field                  | Type     | Description                           |
|------------------------|----------|---------------------------------------|
| `path`                 | string   | Absolute path to the scanned repo     |
| `detected_languages`   | string[] | Programming languages found           |
| `detected_project_types`| string[]| Project types detected                |

## `summary` object

| Field    | Type   | Description                                      |
|----------|--------|--------------------------------------------------|
| `score`  | int    | Reproducibility score (0-100)                    |
| `status`         | string | Overall status: `"pass"`, `"warn"`, or `"fail"` |
| `counts`         | object | Counts by severity level                         |
| `score_breakdown`| array  | Per-check deduction details                      |

### `summary.counts` object

| Field     | Type | Description                    |
|-----------|------|--------------------------------|
| `info`    | int  | Number of info-level findings  |
| `warning` | int  | Number of warnings             |
| `error`   | int  | Number of errors               |

### `summary.score_breakdown` array items

| Field      | Type   | Description                                |
|------------|--------|--------------------------------------------|
| `id`       | string | Check ID (e.g., `"META001"`)               |
| `title`    | string | Check title                                |
| `severity` | string | Severity level                             |
| `status`   | string | Check outcome                              |
| `deduction`| int    | Points deducted from score                 |

## `metadata` object

| Field            | Type     | Description                               |
|------------------|----------|-------------------------------------------|
| `generated_at`   | string   | ISO 8601 timestamp of the scan            |
| `scanned_files`  | int      | Number of files scanned                   |
| `ignored_paths`  | string[] | Paths excluded from scanning              |

## `checks` array items

Each item in the `checks` array is a `CheckResult` object:

| Field           | Type     | Description                                      |
|-----------------|----------|--------------------------------------------------|
| `id`            | string   | Check identifier (e.g., `"META001"`)             |
| `title`         | string   | Human-readable check title                       |
| `category`      | string   | Check category (e.g., `"META"`, `"ENV"`)         |
| `severity`      | string   | Severity level (see enums below)                 |
| `status`        | string   | Check outcome (see enums below)                  |
| `message`       | string   | Description of what was found                    |
| `evidence`      | string[] | Files or patterns that triggered the result      |
| `recommendation`| string   | Actionable advice (empty if check passed)        |

## Enums

### Status

| Value     | Meaning                                         |
|-----------|-------------------------------------------------|
| `"pass"`  | Check passed                                    |
| `"warn"`  | Check produced a warning                        |
| `"fail"`  | Check failed                                    |
| `"unknown"`| Check could not determine the result           |

### Severity

| Value       | Meaning                                      |
|-------------|----------------------------------------------|
| `"info"`    | Informational, lowest priority               |
| `"warning"` | Should be addressed but not blocking         |
| `"error"`   | Must be addressed for reproducibility        |

## Example report

```json
{
  "schema_version": "0.2",
  "tool": "oss-paper-ci",
  "version": "0.2.0",
  "metadata": {
    "generated_at": "2026-06-07T12:00:00+00:00",
    "scanned_files": 42,
    "ignored_paths": [".git", ".venv", "node_modules", "__pycache__"]
  },
  "repository": {
    "path": "/home/user/my-paper",
    "detected_languages": ["Python", "LaTeX"],
    "detected_project_types": ["Python package", "LaTeX"]
  },
  "summary": {
    "score": 62,
    "status": "warn",
    "counts": {
      "info": 8,
      "warning": 5,
      "error": 0
    },
    "score_breakdown": [
      {
        "id": "META003",
        "title": "Citation information exists",
        "severity": "warning",
        "status": "warn",
        "deduction": 1
      },
      {
        "id": "ENV002",
        "title": "Lock file exists",
        "severity": "warning",
        "status": "warn",
        "deduction": 1
      }
    ]
  },
  "checks": [
    {
      "id": "META001",
      "title": "README file exists",
      "category": "META",
      "severity": "error",
      "status": "pass",
      "message": "Found README.md.",
      "evidence": ["README.md"],
      "recommendation": ""
    },
    {
      "id": "META002",
      "title": "LICENSE file exists",
      "category": "META",
      "severity": "error",
      "status": "pass",
      "message": "Found LICENSE.",
      "evidence": ["LICENSE"],
      "recommendation": ""
    },
    {
      "id": "META003",
      "title": "Citation information exists",
      "category": "META",
      "severity": "warning",
      "status": "warn",
      "message": "No citation information found.",
      "evidence": [],
      "recommendation": "Add a CITATION.cff file or a 'Citation' section to your README."
    }
  ],
  "recommendations": [
    "Add a CITATION.cff file or a 'Citation' section to your README.",
    "Add a lock file for reproducible dependency resolution."
  ],
  "blocking_issues": []
}
```

## Score calculation

The score uses a deduction model starting at 100:

- Each non-passing check deducts points based on its severity and status.
- Per-category deductions are capped to prevent cascading penalties.
- Critical checks (META001, META002, ENV001) carry extra penalties on failure.

### Deduction table

| Severity | Status  | Deduction |
|----------|---------|-----------|
| error    | fail    | 5         |
| error    | warn    | 2         |
| error    | unknown | 3         |
| warning  | fail    | 4         |
| warning  | warn    | 1         |
| warning  | unknown | 1         |
| info     | fail    | 2         |
| info     | unknown | 0         |
| info     | pass    | 0         |

### Category caps

| Category | Max deduction |
|----------|---------------|
| META     | 20            |
| ENV      | 20            |
| EXP      | 15            |
| DATA     | 10            |
| RES      | 8             |
| PAP      | 8             |
| CI       | 8             |

### Status determination

| Condition                                  | Status |
|--------------------------------------------|--------|
| Score < 50 OR any error-level check failed | `"fail"` |
| Any failure OR any warning OR score < 80   | `"warn"` |
| Otherwise                                  | `"pass"` |
