# Batch Diff

Compare two batch scan reports to see what changed between runs.

## Usage

```bash
# Markdown output
oss-paper-ci batch diff --old old-batch.json --new new-batch.json --format markdown

# JSON output
oss-paper-ci batch diff --old old-batch.json --new new-batch.json --format json --output diff.json
```

## Diff Output

The diff includes:

- **project_added**: Projects present in new but not old
- **project_removed**: Projects present in old but not new
- **project_diffs**: Per-project score and status changes
- **new_failures**: Projects that went from pass/warn to fail
- **resolved_failures**: Projects that went from fail to pass/warn
- **average_score_delta**: Change in average score across all projects

## Example Output (Markdown)

```markdown
# Batch Report Diff

## Summary

| Metric | Old | New | Delta |
|--------|-----|-----|-------|
| Projects | 3 | 3 | +0 |
| Average Score | 85.0 | 88.3 | +3.3 |

## Project Changes

| Project | Old Score | New Score | Delta | Old Status | New Status |
|---------|-----------|-----------|-------|------------|------------|
| project-a | 80 | 93 | +13 | warn | pass |
```

## Notes

- Diff compares by project ID
- Cache status is not considered in the semantic diff
- Diff works with any two batch JSON reports, regardless of cache state
