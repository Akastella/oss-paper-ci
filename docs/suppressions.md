# Suppressions

Suppressions allow you to ignore specific findings with a documented
reason.  This is useful for legacy code, known issues, or false positives.

## Configuration-Level Suppressions

Add suppressions to your `.oss-paper-ci.yml`:

```yaml
suppressions:
  paths:
    - "legacy/**"
    - "vendor/**"
  findings:
    - id: LAB002
      reason: "Legacy fixture does not keep result documentation."
      until: "2027-01-01"
    - id: META005
      reason: "Not applicable to single-author project."
```

### Fields

#### `paths`

List of glob patterns.  Findings whose evidence matches these paths
are suppressed.

```yaml
suppressions:
  paths:
    - "legacy/**"
    - "tests/fixtures/**"
```

#### `findings`

List of finding suppressions by check ID.

| Field | Required | Description |
|-------|----------|-------------|
| `id` | Yes | Check ID to suppress (e.g., LAB002) |
| `reason` | Yes* | Why this finding is suppressed |
| `until` | No | Expiration date (YYYY-MM-DD) |

*The `reason` field is required for all profiles except `lenient`.

## How Suppressions Work

1. After all checks run, suppressions are applied.
2. Suppressed findings are removed from the active check list.
3. Suppressed findings appear in the report's `suppressed_findings` field.
4. Suppressed findings do **not** affect the score or status.

## Report Output

Suppressed findings appear in the JSON report:

```json
{
  "suppressed_findings": [
    {
      "id": "LAB002",
      "title": "Require results README",
      "severity": "warning",
      "status": "fail",
      "message": "results/README.md is missing.",
      "reason": "Legacy fixture does not keep result documentation.",
      "until": "2027-01-01"
    }
  ]
}
```

## CLI Commands

### Validate suppressions

```bash
oss-paper-ci config validate
```

This checks that:
- All suppression entries have an `id`
- All entries have a `reason` (except lenient profile)
- The config file is valid

### View suppressions

```bash
oss-paper-ci config explain
```

The output includes suppression configuration.

## Best Practices

1. **Always provide a reason**: Suppressions without reasons are
   untraceable and become technical debt.

2. **Use expiration dates**: Set `until` to review suppressions
   periodically.

3. **Don't suppress crashes**: Suppressions are for legitimate findings,
   not for hiding tool errors.

4. **Review in CI**: Include suppression review in your PR process.

5. **Document in README**: If your project has many suppressions,
   explain why in your README.

## Example

```yaml
# .oss-paper-ci.yml
version: 1
profile: strict

suppressions:
  paths:
    - "legacy/**"
  findings:
    - id: DATA001
      reason: "Data is hosted externally, not in the repository."
      until: "2027-06-01"
    - id: EXP002
      reason: "Experiment uses proprietary software, cannot script."
```

## Limitations

- Suppressions are global per scan, not per-file.
- No inline comment suppression (planned for future release).
- Suppressed findings still appear in the report for traceability.
- Suppressions cannot hide tool crashes or unknown errors.
