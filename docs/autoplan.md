# Autoplan

Autoplan generates a candidate `reproducibility.yml` from repository analysis. The candidate plan **requires human review** before execution; autoplan does not execute inferred commands or modify the repository without explicit `--write`.

## Usage

```bash
# Generate candidate plan (output to stdout)
oss-paper-ci autoplan .

# Write candidate plan to file
oss-paper-ci autoplan . --output candidate-reproducibility.yml

# Write candidate plan to repository (explicit opt-in)
oss-paper-ci autoplan . --write --output reproducibility.yml

# Force overwrite existing file
oss-paper-ci autoplan . --write --output reproducibility.yml --force

# Output as JSON
oss-paper-ci autoplan . --format json

# Output as Markdown
oss-paper-ci autoplan . --format markdown
```

## Subcommands

### generate

Generate a candidate reproducibility plan.

```bash
oss-paper-ci autoplan generate .
oss-paper-ci autoplan .  # shorthand
```

### validate

Validate a candidate reproducibility.yml file.

```bash
oss-paper-ci autoplan validate candidate-reproducibility.yml
```

Checks for:
- Required fields (`schema_version`, `commands[].id`, `commands[].run`)
- Unique command IDs
- Valid YAML structure

### diff

Compare two reproducibility.yml files.

```bash
oss-paper-ci autoplan diff --old reproducibility.yml --new candidate-reproducibility.yml
```

Shows added, removed, and changed sections.

### explain

Explain a reproducibility config file.

```bash
oss-paper-ci autoplan explain reproducibility.yml
```

Shows environment, commands, artifacts, safety, and limitations in human-readable format.

## Candidate Config Structure

The generated candidate config follows the reproducibility.yml v0.2 schema:

```yaml
schema_version: "0.2"
generated_by: oss-paper-ci
generated_mode: candidate
confidence: 0.74

environment:
  type: python
  python: ">=3.10"
  install:
    - python -m pip install -r requirements.txt

commands:
  - id: train
    run: python scripts/train.py
    timeout_seconds: 300
    expected_artifacts:
      - results/metrics.json

artifacts:
  - path: results/metrics.json
    type: metrics

metrics: []

safety:
  network: false
  allow_shell: false
  max_runtime_seconds: 600
  max_artifact_mb: 20

limitations:
  - Candidate plan inferred from repository files; review before execution.
```

### Key Fields

- `generated_mode: candidate` -- Marks this as an auto-generated plan
- `confidence` -- Overall confidence score (0.0-1.0)
- `commands` -- Ordered list of commands with IDs and timeouts
- `artifacts` -- Expected output artifacts with types
- `safety` -- Execution safety constraints

## Confidence Scoring

Confidence scores are computed from:
- **Environment** (0.3 weight): Ecosystem detection, environment files, runtime availability
- **Commands** (0.4 weight): Number and quality of extracted commands
- **Artifacts** (0.2 weight): Detected result/figure/metrics files
- **Metrics** (0.1 weight): Whether metrics files exist

See [autoplan-confidence.md](autoplan-confidence.md) for details.

## Safety

- Autoplan **does not execute** commands by default
- `--write` is required to write the candidate config
- `--force` is required to overwrite an existing file
- All generated configs are marked `generated_mode: candidate`
- Dangerous commands are excluded from the candidate plan
- No network access is performed (except explicit `--clone`)
- No dependencies are installed

## Workflow

The typical workflow for using autoplan:

1. **Analyze**: `oss-paper-ci intake .` -- Understand the repository
2. **Plan**: `oss-paper-ci autoplan . --output candidate.yml` -- Generate candidate
3. **Review**: Human reviews the candidate plan
4. **Adopt**: `oss-paper-ci autoplan . --write --output reproducibility.yml --force` -- Write config
5. **Verify**: `oss-paper-ci reproduce plan .` -- Generate execution plan
6. **Execute**: `oss-paper-ci reproduce run . --execute --sandbox local` -- Run with safety gates

## Limitations

- Candidate plans are inferred from repository files; they may not be correct
- Command ordering may not reflect actual dependency requirements
- Timeout values are defaults; adjust based on expected runtime
- Not all detected commands may be needed for reproduction
- Environment detection is based on file presence, not content analysis
- The tool does not guarantee that the generated plan will lead to successful reproduction

## See Also

- [Repository Intake](repository-intake.md) -- Analyze repository structure
- [Autoplan Confidence](autoplan-confidence.md) -- How confidence scores work
- [Reproduction Orchestrator](reproduction-orchestrator.md) -- Execute reproduction plans
- [Autoplan Review Workflow](autoplan-review-workflow.md) -- Recommended review process
