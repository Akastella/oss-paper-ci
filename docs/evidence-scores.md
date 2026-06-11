# Evidence Scores

OSS-Paper-CI computes evidence scores as engineering readiness indicators.
These are NOT scientific correctness scores.

## Score Components

| Component | What it measures |
|-----------|-----------------|
| `readiness_score` | Overall engineering readiness (0-100) |
| `data_evidence_score` | Data documentation and availability |
| `execution_evidence_score` | Experiment scripts and commands |
| `artifact_evidence_score` | Results, figures, metrics presence |
| `provenance_score` | Metadata, license, citation |

## How Scores Are Computed

Each component is based on check results in that category:
- **data**: DATA001-DATA006 checks
- **execution**: EXP001-EXP006 checks
- **artifact**: RES001-RES005 checks
- **provenance**: META001-META007 checks

Deductions are applied per check based on severity and status.
Category caps prevent one category from dominating the score.

## What Scores Mean

- **High score (80-100)**: Good engineering practices for reproducibility
- **Medium score (50-79)**: Some engineering basics are missing
- **Low score (0-49)**: Significant engineering gaps

## What Scores Do NOT Mean

- A high score does NOT mean the paper is correct
- A high score does NOT mean results will be reproducible
- A low score does NOT mean the research is flawed
- A low score does NOT mean the paper should be rejected

## Score in Reports

The score components appear in:
- Scan JSON report: `summary.score_components`
- Dossier: executive summary
- Markdown/HTML reports: score breakdown section

## See Also

- [Data Diagnostics](data-diagnostics.md)
- [Result Validation](result-validation.md)
- [Limitations](limitations.md)
