# Report Formats

oss-paper-ci supports multiple output formats for different use cases.

## Markdown

Human-readable report with tables, scores, and recommendations.

```bash
oss-paper-ci scan --format markdown -o report.md
```

**Use cases:** CI artifacts, PR comments, human review.

## JSON

Structured output for programmatic access.

```bash
oss-paper-ci scan --format json -o report.json
```

**Use cases:** CI gates, score thresholds, custom tooling.

See [report-schema.md](report-schema.md) for the full JSON schema.

## SARIF

Static Analysis Results Interchange Format v2.1.0 for GitHub Code Scanning.

```bash
oss-paper-ci scan --format sarif -o results.sarif
```

**Use cases:** GitHub Security tab, VS Code SARIF Viewer, security dashboards.

See [sarif.md](sarif.md) for SARIF format details.

## DOT (Graphviz)

Evidence graph in DOT format for visualization.

```bash
oss-paper-ci graph --format dot -o graph.dot --show-orphans
```

**Use cases:** Visualizing file dependencies, identifying orphan files.

Render with: `dot -Tpng graph.dot -o graph.png`

## Graph JSON

Evidence graph in JSON format.

```bash
oss-paper-ci graph --format json -o graph.json
```

**Use cases:** Programmatic graph analysis, custom visualizations.

## Graph Markdown

Evidence graph in Markdown table format.

```bash
oss-paper-ci graph --format markdown -o graph.md
```

**Use cases:** Quick review in CI artifacts or PR comments.

## Smoke output

Smoke runner output (text or JSON).

```bash
oss-paper-ci smoke --format text
oss-paper-ci smoke --format json
```

**Use cases:** Verifying experiment commands work, checking security policy.
