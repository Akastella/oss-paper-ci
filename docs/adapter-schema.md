# Adapter Report Schema

The adapter report schema defines the JSON structure produced by `oss-paper-ci adapters inspect`.

## Schema Version

Current schema version: `0.1`

## Report Structure

```json
{
  "schema_version": "0.1",
  "report_type": "oss-paper-ci-language-adapter-report",
  "tool_version": "3.5.0rc1",
  "path": ".",
  "detected_adapters": [
    {
      "name": "python",
      "display_name": "Python",
      "confidence": 0.9,
      "evidence": ["pyproject.toml", "main.py"],
      "runtime": {
        "name": "python3",
        "available": true,
        "version": "Python 3.12.0",
        "path": "/usr/bin/python3"
      },
      "supports_dry_run": true,
      "supports_execute": true,
      "limitations": [],
      "warnings": []
    }
  ],
  "recommended_adapter": "python",
  "warnings": [],
  "limitations": []
}
```

## Fields

### Top-level Fields

| Field | Type | Description |
|-------|------|-------------|
| `schema_version` | string | Schema version |
| `report_type` | string | Report type identifier |
| `tool_version` | string | oss-paper-ci version |
| `path` | string | Scanned repository path |
| `detected_adapters` | array | List of detected adapters |
| `recommended_adapter` | string | Recommended adapter name |
| `warnings` | array | Global warnings |
| `limitations` | array | Global limitations |

### Detection Object

| Field | Type | Description |
|-------|------|-------------|
| `name` | string | Adapter identifier |
| `display_name` | string | Human-readable name |
| `confidence` | float | Detection confidence (0.0-1.0) |
| `evidence` | array | Files that triggered detection |
| `runtime` | object | Runtime availability info |
| `supports_dry_run` | boolean | Whether dry-run is supported |
| `supports_execute` | boolean | Whether execution is supported |
| `limitations` | array | Adapter-specific limitations |
| `warnings` | array | Adapter-specific warnings |

### Runtime Object

| Field | Type | Description |
|-------|------|-------------|
| `name` | string | Runtime command name |
| `available` | boolean | Whether runtime is installed |
| `version` | string | Runtime version (if available) |
| `path` | string | Path to runtime binary |
| `error` | string | Error message (if detection failed) |

## Validation

Use `oss-paper-ci adapters validate PATH` to check report validity.

## Notes

- Confidence values are relative; higher means more evidence found
- `recommended_adapter` prefers adapters with available runtimes
- Missing runtime does not indicate an error — it's a diagnostic result
