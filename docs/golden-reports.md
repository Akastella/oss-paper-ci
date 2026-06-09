# Golden Reports

Golden reports are normalized JSON files that capture the expected output
of a scan.  They are used for compatibility testing to ensure that
changes to the scoring engine or check logic don't accidentally change
results.

## Purpose

Golden reports serve as **compatibility snapshots**, not quality proofs.
They answer: "Did this change alter the output?" — not "Is the output
correct?"

## How They Work

1. A scan is run against a known fixture with a known profile.
2. The JSON report is normalized (timestamps, absolute paths removed).
3. The normalized report is saved as a golden file.
4. Future runs compare against the golden file.
5. Mifferences indicate a change that needs review.

## Golden Files

Located in `tests/golden/`:

| File | Fixture | Profile |
|------|---------|---------|
| `realistic_ml_default.json` | realistic_ml_repo | default |
| `realistic_ml_strict.json` | realistic_ml_repo | strict |
| `demo_paper_publication.json` | demo-paper-repo | publication |

## Updating Golden Reports

When you intentionally change scoring or check behavior:

```bash
# Regenerate all golden reports
python scripts/update_golden_reports.py

# Check without updating (CI mode)
python scripts/update_golden_reports.py --check
```

## Normalization

Golden reports are normalized to remove unstable fields:

- `metadata.generated_at` → replaced with `"NORMALIZED"`
- `repository.path` → replaced with `"NORMALIZED"`
- Absolute paths in evidence → made relative

This ensures that golden reports are stable across environments and runs.

## CI Integration

```yaml
- name: Check golden reports
  run: python scripts/update_golden_reports.py --check
```

If the golden reports don't match, the CI fails with a diff showing
what changed.

## When to Update

Update golden reports when:

- You intentionally change scoring weights
- You add or modify check logic
- You change the report format
- You update policy profile thresholds

Do **not** update golden reports to hide unexpected changes.

## Limitations

- Golden reports are snapshots, not guarantees of correctness.
- They only cover the specific fixtures and profiles tested.
- They don't validate that the output is "right" — only that it's stable.
- Normalization may mask real differences if too aggressive.
