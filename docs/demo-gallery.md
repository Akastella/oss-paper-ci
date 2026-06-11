# Demo Gallery

Example reports and outputs from oss-paper-ci.

## Scan Reports

| Report | Format | Description |
|--------|--------|-------------|
| [Scan Report (Markdown)](../examples/reports/realistic_ml_report.md) | Markdown | Full scan with findings |
| [Scan Report (JSON)](../examples/reports/realistic_ml_report.json) | JSON | Machine-readable scan result |
| [HTML Report](../examples/reports/demo_paper_report.html) | HTML | Single-file HTML report |
| [SARIF Output](../examples/reports/realistic_ml.sarif) | SARIF | GitHub Code Scanning format |

## Reproduction Reports

| Report | Format | Description |
|--------|--------|-------------|
| [Dry-run Report](../examples/reports/reproduce_demo_dry_run.md) | Markdown | Safe dry-run reproduction |
| [Execute Report](../examples/reports/reproduce_demo_report.md) | Markdown | Executed reproduction |
| [Execute Report (JSON)](../examples/reports/reproduce_demo_report.json) | JSON | Machine-readable |
| [Execute Report (HTML)](../examples/reports/reproduce_demo_report.html) | HTML | Single-file HTML |

## Capsule Reports

| Report | Format | Description |
|--------|--------|-------------|
| [Capsule Verify](../examples/reports/reproduce_capsule_verify.md) | Markdown | Verification result |
| [Capsule Inspect](../examples/reports/reproduce_capsule_inspect.md) | Markdown | Capsule metadata |
| [Capsule Manifest](../examples/reports/reproduce_capsule_manifest.json) | JSON | Full manifest |
| [Capsule Diff](../examples/reports/reproduce_capsule_diff.md) | Markdown | Two capsules compared |

## Batch Reports

| Report | Format | Description |
|--------|--------|-------------|
| [Batch Report](../examples/reports/batch_demo_report.md) | Markdown | Multi-project scan |
| [Batch Report (JSON)](../examples/reports/batch_demo_report.json) | JSON | Machine-readable |
| [Batch Report (HTML)](../examples/reports/batch_demo_report.html) | HTML | Single-file HTML |
| [Batch Diff](../examples/reports/batch_diff.md) | Markdown | Batch comparison |

## Other Reports

| Report | Format | Description |
|--------|--------|-------------|
| [Evidence Graph](../examples/reports/realistic_ml_graph.md) | Markdown | File dependencies |
| [Baseline Compare](../examples/reports/realistic_ml_baseline_compare.md) | Markdown | Regression detection |
| [Smoke Run](../examples/reports/realistic_ml_smoke.md) | Markdown | Safe experiment run |
| [PR Comment](../examples/reports/demo_paper_pr_comment.md) | Markdown | GitHub PR comment |
| [Custom Rules](../examples/reports/custom_rules_report.md) | Markdown | Rule pack results |
| [Policy Diff](../examples/reports/policy_diff.md) | Markdown | Profile comparison |

## Terminal Examples

| Example | Description |
|---------|-------------|
| [Wizard Output](../examples/terminal/wizard_output.txt) | Guided wizard plain output |
| [Workbench Output](../examples/terminal/workbench_plain_output.txt) | Workbench pipeline plain output |
| [Theme Preview](../examples/terminal/theme_preview.md) | Theme preview with sample data |
| [Pretty Preview](../examples/terminal/workbench_pretty_preview.md) | Rich terminal output description |

## Example Repositories

- [demo-paper-repo](../examples/demo-paper-repo/) — minimal paper repository
- [demo-reproduce-repo](../examples/demo-reproduce-repo/) — reproduction target

## Example Workflows

- [examples/github-actions/](../examples/github-actions/) — 20+ workflow templates
- [examples/rule-packs/](../examples/rule-packs/) — custom rule pack examples
- [examples/workspaces/](../examples/workspaces/) — workspace configurations
