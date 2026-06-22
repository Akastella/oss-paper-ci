# Autoplan Review Workflow

This document describes the recommended workflow for reviewing and adopting auto-generated reproducibility plans.

## Step 1: Intake Analysis

Start by analyzing the repository:

```bash
oss-paper-ci intake . --format markdown --output intake-report.md
```

Review the intake report:
- Check detected ecosystems
- Review command candidates
- Note confidence scores
- Check for flagged dangerous commands

## Step 2: Generate Candidate Plan

Generate the candidate reproducibility plan:

```bash
oss-paper-ci autoplan . --output candidate-reproducibility.yml
```

## Step 3: Review Candidate Plan

Review the candidate plan carefully:

### Environment Section
- Is the ecosystem type correct?
- Are the install commands appropriate?
- Are there missing dependencies?

### Commands Section
- Are the commands in the right order?
- Are timeout values reasonable?
- Are there missing commands?
- Are there unnecessary commands?

### Artifacts Section
- Are the expected artifacts correct?
- Are there missing artifacts?
- Are artifact types correct?

### Safety Section
- Is `network: false` appropriate?
- Is `allow_shell: false` appropriate?
- Are timeout values reasonable?

### Confidence Scores
- Overall confidence ≥ 0.7 is generally acceptable
- Lower confidence may need more manual review

## Step 4: Validate

Validate the candidate plan:

```bash
oss-paper-ci autoplan validate candidate-reproducibility.yml
```

Fix any validation errors before proceeding.

## Step 5: Diff with Existing Config

If an existing config exists, compare:

```bash
oss-paper-ci autoplan diff --old reproducibility.yml --new candidate-reproducibility.yml
```

Review the differences and merge as needed.

## Step 6: Adopt

When satisfied with the candidate plan:

```bash
oss-paper-ci autoplan . --write --output reproducibility.yml --force
```

## Step 7: Verify with Orchestrator

Verify the plan works with the reproduction orchestrator:

```bash
oss-paper-ci reproduce plan .
```

This generates an execution plan without running commands.

## Step 8: Execute (Optional)

If you want to actually run the reproduction:

```bash
oss-paper-ci reproduce run . --execute --sandbox local
```

## CI Integration

For CI/CD integration, see the GitHub Actions examples:
- `examples/github-actions/intake-autoplan.yml`
- `examples/github-actions/autoplan-review-artifact.yml`

These workflows generate candidate plans as artifacts for manual review.

## Important Notes

- **Always review** the candidate plan before adoption
- **Never blindly trust** auto-generated plans
- **Confidence scores** indicate detection quality, not correctness
- **Test the plan** in a safe environment before production use
- **Document changes** you make to the candidate plan
