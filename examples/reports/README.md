# Example Reports

These reports were generated from the `tests/fixtures/realistic_ml_repo` test
fixture using oss-paper-ci v1.2.0rc1.

**Important:** These are synthetic test fixtures, not real external repositories.
They are included to demonstrate output formats. No adoption claims are made.

## Files

| File | Command | Format |
|------|---------|--------|
| `realistic_ml_report.md` | `oss-paper-ci scan --format markdown` | Markdown scan report |
| `realistic_ml_report.json` | `oss-paper-ci scan --format json` | JSON scan report |
| `realistic_ml_graph.md` | `oss-paper-ci graph --format markdown` | Evidence graph (Markdown) |
| `realistic_ml_graph.json` | `oss-paper-ci graph --format json` | Evidence graph (JSON) |
| `realistic_ml_graph.dot` | `oss-paper-ci graph --format dot` | Evidence graph (DOT/Graphviz) |
| `realistic_ml_baseline.json` | `oss-paper-ci baseline create` | Baseline snapshot |
| `realistic_ml_baseline_compare.md` | `oss-paper-ci baseline compare` | Baseline regression report |
| `realistic_ml_smoke.md` | `oss-paper-ci smoke --format text` | Smoke run report |
| `realistic_ml.sarif` | `oss-paper-ci scan --format sarif` | SARIF for GitHub Code Scanning |

## Reproduce

To regenerate these reports from your own repository:

```bash
oss-paper-ci scan /path/to/your/repo --format markdown --output report.md
oss-paper-ci scan /path/to/your/repo --format json --output report.json
oss-paper-ci graph /path/to/your/repo --format json --output graph.json
oss-paper-ci baseline create /path/to/your/repo --output baseline.json
oss-paper-ci baseline compare /path/to/your/repo --baseline baseline.json
oss-paper-ci smoke /path/to/your/repo --dry-run
```
