# Evidence Report Schema

The evidence report follows a structured JSON schema.

## Schema Version

`schema_version`: "0.1"

## Top-Level Fields

| Field | Type | Description |
|-------|------|-------------|
| `schema_version` | string | Schema version |
| `report_type` | string | Always "oss-paper-ci-evidence-report" |
| `tool_version` | string | oss-paper-ci version |
| `profile` | string | "reviewer", "author", or "maintainer" |
| `repo` | string | Repository name (relative, not absolute) |
| `summary` | object | High-level summary |
| `sections` | object | Detailed sections |
| `findings` | array | Aggregated findings |
| `recommended_next_steps` | array | Profile-specific recommendations |
| `limitations` | array | What this report does NOT verify |

## Summary Object

| Field | Type | Description |
|-------|------|-------------|
| `status` | string | "pass", "warn", or "fail" |
| `readiness_score` | int | 0-100 score |
| `risk_level` | string | "low", "medium", or "high" |
| `total_findings` | int | Number of findings |
| `findings_high` | int | High-severity findings |
| `findings_medium` | int | Medium-severity findings |
| `plain_language_summary` | string | Human-readable summary |

## Sections

### repository
- `path`: Repository name (relative)
- `commit`: Git commit SHA (if available)
- `dirty`: Whether working directory has changes

### reproducibility
- `score`: 0-100 readiness score
- `status`: "pass", "warn", or "fail"
- `checks_total`, `checks_pass`, `checks_warn`, `checks_fail`
- `policy`: Active policy profile
- `score_components`: Per-category scores
- `findings`: Failing/warning checks

### data
- `checks_total`, `checks_missing`
- `checks[]`: Individual data diagnostics

### results
- `checks_total`, `checks_missing`, `checks_invalid`
- `checks[]`: Individual result validations

### ecosystems
- `detected[]`: Detected language ecosystems
- `total`: Count

### trust
- `summary`: Trust report summary
- `findings_count`, `findings_high`, `findings_medium`, `findings_low`
- `findings[]`: Trust/security findings

### adoption
- `missing_files[]`: Files that should exist
- `recommended_files[]`: Recommended additions
- `manual_steps[]`: Suggested manual actions

## Finding Object

| Field | Type | Description |
|-------|------|-------------|
| `id` | string | Finding identifier |
| `severity` | string | "info", "warning", "error", "high", "medium", "low" |
| `category` | string | "reproducibility", "data", "results", "trust", "security" |
| `title` | string | Short description |
| `message` | string | Detailed message |
| `recommendation` | string | Suggested fix (optional) |
| `path` | string | Relative file path (optional) |
| `source_section` | string | Which section produced this |

## Path Handling

All paths in the report are relative to the repository root. No absolute paths are included.
