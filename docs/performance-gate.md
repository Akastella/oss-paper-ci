# Performance Gate

The performance gate measures scan runtime for test fixtures and
reports results.  It helps detect performance regressions in CI.

## Usage

```bash
# Markdown output
python scripts/performance_gate.py --format markdown --output performance.md

# JSON output
python scripts/performance_gate.py --format json --output performance.json

# With time budget
python scripts/performance_gate.py --max-seconds 30
```

## What It Measures

- Scan runtime per fixture
- Total runtime across all fixtures
- Whether any fixture exceeds the time budget

## Fixtures

The performance gate runs against these test fixtures:

| Fixture | Description |
|---------|-------------|
| minimal_bad_repo | Minimal repo with almost nothing |
| broken_paper_repo | Paper repo with broken structure |
| paper_ready_repo | Well-structured paper repo |
| realistic_ml_repo | Realistic ML project |

## Output

### Markdown

```markdown
# Performance Gate Results

| Fixture | Runtime (s) | Status |
|---------|-------------|--------|
| minimal_bad_repo | 0.12 | PASS |
| broken_paper_repo | 0.15 | PASS |
| paper_ready_repo | 0.18 | PASS |
| realistic_ml_repo | 0.22 | PASS |

**Total:** 0.67s
**Budget:** 30.0s
**Result:** PASS
```

### JSON

```json
{
  "fixtures": [
    {"name": "minimal_bad_repo", "runtime_seconds": 0.12, "status": "PASS"},
    {"name": "broken_paper_repo", "runtime_seconds": 0.15, "status": "PASS"}
  ],
  "total_seconds": 0.67,
  "budget_seconds": 30.0,
  "passed": true
}
```

## CI Integration

```yaml
- name: Performance gate
  run: python scripts/performance_gate.py --max-seconds 30 --format json --output performance.json
```

## Important Notes

- **Not an academic benchmark**: This is an engineering regression tool,
  not a performance study.
- **CI-friendly**: Default budget is generous to avoid flaky failures.
- **No network**: The gate only runs local scans.
- **No user scripts**: Only oss-paper-ci's own fixtures are used.
- **Optional**: The gate is not required for release, but recommended
  for catching regressions.

## Tuning

If your CI environment is slow, increase the budget:

```bash
python scripts/performance_gate.py --max-seconds 60
```

If you want strict performance requirements:

```bash
python scripts/performance_gate.py --max-seconds 10
```
