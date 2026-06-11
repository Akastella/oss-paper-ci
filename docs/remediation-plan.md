# Remediation Plan

The remediation plan converts findings into actionable steps.

## Priority Levels

| Priority | Meaning | Example |
|----------|---------|---------|
| P0 | Blocking — must fix | Missing environment file |
| P1 | Important — should fix | Missing data documentation |
| P2 | Recommended | Add citation info |
| P3 | Nice-to-have | Add more detailed README |

## Effort Levels

| Effort | Meaning |
|--------|---------|
| low | Can be done in minutes |
| medium | Requires some work |
| high | Significant effort |

## How It's Built

The remediation plan is constructed from:
- Scan report findings (errors → P0, warnings → P1)
- Reproduce report failures
- Risk register entries

## Important Notes

- The plan suggests actions, not patches
- It does not modify your repository
- It provides suggested file paths and verification commands
- Priority is based on impact on reproducibility, not scientific quality

## See Also

- [Dossier](dossier.md)
- [Evidence Map](evidence-map.md)
