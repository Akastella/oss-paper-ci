# Reproducibility Dossier

A reproducibility dossier is a structured document that summarizes
the reproducibility evidence in a repository, identifies risks,
and provides actionable remediation steps.

## Quick Start

```bash
# Generate an author dossier from a scan report
oss-paper-ci dossier --scan-report report.json --audience author

# Generate a reviewer dossier
oss-paper-ci dossier --scan-report report.json --audience reviewer

# Generate a Chinese dossier
oss-paper-ci dossier --scan-report report.json --language zh-CN

# Generate an issue checklist
oss-paper-ci dossier --scan-report report.json --format issue --output issue.md
```

## Command Reference

```bash
oss-paper-ci dossier [OPTIONS]
```

| Option | Description |
|--------|-------------|
| `--scan-report PATH` | Scan JSON report |
| `--reproduce-report PATH` | Reproduce JSON report |
| `--capsule PATH` | Capsule zip file |
| `--workspace-report PATH` | Workspace/batch JSON report |
| `--repo PATH` | Repository path (runs scan internally) |
| `--audience ROLE` | author, reviewer, maintainer (default: author) |
| `--language LANG` | en, zh-CN, ja (default: en) |
| `--format FORMAT` | markdown, json, html, issue, pr-comment |
| `--output FILE` | Write to file |

## What's in a Dossier

### Executive Summary

A plain-language overview of the repository's reproducibility status.

### Evidence Map

A structured inventory of what reproducibility evidence exists
(and what's missing) across categories: metadata, environment,
data, execution, results, provenance, automation.

### Risk Register

A prioritized list of reproducibility risks with severity,
likelihood, impact, and mitigation suggestions.

### Remediation Plan

Actionable steps to improve reproducibility, ordered by priority
(P0 = blocking, P1 = important, P2 = recommended, P3 = nice-to-have).

### Audience-Specific Output

- **Author**: checklist of what to fix
- **Reviewer**: summary of available evidence
- **Maintainer**: roadmap for organization-wide governance

## See Also

- [Evidence Map](evidence-map.md)
- [Remediation Plan](remediation-plan.md)
- [Roles](roles.md)
