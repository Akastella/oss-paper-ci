# Report Diff

The `diff` command compares two scan report JSON files without running
a live scan.  This is useful for:

- CI pipelines that compare current results against a previous run
- Manual review of how changes affected reproducibility score
- Tracking progress over time

## Usage

```bash
oss-paper-ci diff --old old-report.json --new new-report.json
oss-paper-ci diff --old old-report.json --new new-report.json --format json
oss-paper-ci diff --old old-report.json --new new-report.json --output diff.md
```

## Output Fields

| Field | Description |
|-------|-------------|
| `score_delta` | Change in score (new - old) |
| `old_score` / `new_score` | Individual scores |
| `old_status` / `new_status` | Individual statuses |
| `status_changed` | Whether status changed |
| `new_findings` | Checks that now fail/warn but didn't before |
| `resolved_findings` | Checks that no longer fail/warn |
| `severity_worsened` | Checks whose status got worse |
| `severity_improved` | Checks whose status got better |
| `changed_categories` | Categories with different check results |
| `recommendation` | Human-readable summary of changes |

## Example

```bash
# Generate two reports
oss-paper-ci scan . --profile lenient --format json --output lenient.json
oss-paper-ci scan . --profile strict --format json --output strict.json

# Compare them
oss-paper-ci diff --old lenient.json --new strict.json --format markdown
```

## CI Integration

```yaml
- name: Compare reports
  run: |
    oss-paper-ci diff --old previous-report.json --new current-report.json \
      --format markdown --output diff-report.md
```

## Notes

- Both files must be valid oss-paper-ci JSON reports
- The diff is structural: it compares check IDs, statuses, and severities
- No external database or server is required
- The diff does not perform statistical significance testing
