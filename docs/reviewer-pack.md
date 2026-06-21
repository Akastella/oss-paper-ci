# Reviewer Pack

The reviewer profile is designed for reviewers, program committees, and anyone evaluating the reproducibility of a scientific repository.

## Usage

```bash
oss-paper-ci evidence . --profile reviewer --format html --output reviewer-report.html
```

## What the Reviewer Pack Provides

- **Readiness score**: Engineering completeness indicator (0-100)
- **Evidence map**: What documentation and artifacts are present or missing
- **Risk register**: Known gaps and their severity
- **Trust assessment**: Supply-chain and workflow security findings
- **Limitations**: Clear statements about what this tool does NOT verify

## What the Reviewer Pack Does NOT Provide

- Scientific correctness judgment
- Paper quality assessment
- Acceptance recommendation
- Novelty evaluation
- Impact prediction

## Interpreting the Score

| Score | Meaning |
|-------|---------|
| 90-100 | Strong reproducibility documentation |
| 70-89 | Adequate with some gaps |
| 50-69 | Significant gaps exist |
| Below 50 | Major reproducibility concerns |

**Important**: A high score does not guarantee the research is correct. A low score does not mean the research is flawed. The score measures engineering completeness of reproducibility artifacts, not scientific merit.

## Recommended Workflow

1. Generate the reviewer report
2. Review the evidence map for completeness
3. Check the risk register for known gaps
4. Note the limitations section
5. Use findings as a starting point for manual review

## See Also

- [evidence-report.md](evidence-report.md) — Report structure
- [author-pack.md](author-pack.md) — Author guidance
- [maintainer-pack.md](maintainer-pack.md) — Maintainer guidance
