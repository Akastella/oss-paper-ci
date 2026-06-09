# Report Diff

## Score Comparison

| Metric | Old | New | Delta |
|--------|-----|-----|-------|
| Score | 65 | 82 | +17 |
| Status | warn | warn | same |

## Policy

- Old profile: default
- New profile: default

## Improved (4)

- **CI001** (CI workflow): fail → pass
- **DATA001** (Data description): fail → warn
- **EXP001** (Experiment script): warn → pass
- **META002** (License): fail → pass

## Changed Categories (4)

- **CI0**: {'pass': 0, 'warn': 0, 'fail': 1} → {'pass': 1, 'warn': 0, 'fail': 0}
- **DAT**: {'pass': 0, 'warn': 0, 'fail': 1} → {'pass': 0, 'warn': 1, 'fail': 0}
- **EXP**: {'pass': 0, 'warn': 1, 'fail': 0} → {'pass': 1, 'warn': 0, 'fail': 0}
- **MET**: {'pass': 1, 'warn': 1, 'fail': 1} → {'pass': 3, 'warn': 1, 'fail': 0}

## Summary

Changes: 4 improved.
