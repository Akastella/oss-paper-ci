# Golden Regression

Golden regression files ensure that oss-paper-ci's evaluation output remains stable across versions.

## Overview

Golden files are "known good" outputs that serve as baselines for comparison. When the tool's output changes intentionally, golden files are updated to reflect the new expected behavior.

## Golden Files

### Evaluation Summary

Location: `tests/golden/evaluation_summary.json`

Contains the complete evaluation output for the corpus, including:
- Version information
- Repository results
- Summary statistics
- Comparison outcomes

### Evaluation Matrix

Location: `tests/golden/evaluation_matrix.md`

Markdown table showing:
- Repository IDs
- Detected ecosystems
- Status
- Score ranges
- Match results

## Using Golden Files

### Running Tests

Tests automatically compare current output against golden files:

```bash
python -m pytest tests/test_evaluation_golden.py -v
```

### Manual Comparison

```bash
oss-paper-ci eval compare \
  --baseline tests/golden/evaluation_summary.json \
  --current examples/reports/evaluation_summary.json
```

### Updating Golden Files

When intentional changes are made:

```bash
# Update golden files to match current output
python scripts/update_evaluation_golden.py

# Verify the update
python -m pytest tests/test_evaluation_golden.py -v
```

## Golden File Format

### JSON Structure

```json
{
  "version": "2.7.0rc1",
  "corpus_dir": "examples/evaluation-corpus",
  "total_repos": 14,
  "repos": [...],
  "summary": {
    "pass": 10,
    "partial": 2,
    "fail": 1,
    "evaluated": 1,
    "error": 0
  }
}
```

### Normalization

Golden files are normalized to:
- Remove absolute paths (use relative)
- Remove timestamps
- Sort repositories alphabetically
- Use consistent formatting

## When to Update

Update golden files when:
- Adding new evaluation fixtures
- Changing expected outcomes
- Modifying scan behavior intentionally
- Updating score calculations

## When NOT to Update

Do NOT update golden files when:
- Tests fail unexpectedly
- Output changes without code changes
- Environment differences cause variation

## Troubleshooting

### Golden comparison fails

1. Check if changes were intentional
2. Review diff output
3. If intentional, update golden files
4. If unintentional, investigate root cause

### Paths in golden files

Golden files use relative paths. If you see absolute paths:
1. Check the generation script
2. Run `python scripts/update_evaluation_golden.py`
3. Verify no absolute paths remain
