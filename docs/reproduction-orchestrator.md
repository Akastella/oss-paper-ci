# Reproduction Orchestrator

The reproduction orchestrator is a plan → execute → verify → report workflow for scientific repositories. It reads `reproducibility.yml`, generates an execution plan, runs declared commands (with explicit authorization), collects artifacts and metrics, and generates verification reports.

## Key principles

- **Default to dry-run:** No code is executed unless you explicitly pass `--execute`.
- **No network access:** The orchestrator does not download data or call external APIs.
- **No auto-install:** Dependencies are not installed unless you explicitly configure it.
- **No repository modification:** The orchestrator does not modify your repository.
- **Not a correctness proof:** The orchestrator verifies that declared steps can be executed and that artifacts/metrics match expectations. It does not prove scientific correctness.

## Commands

| Command | Description |
|---------|-------------|
| `reproduce plan` | Generate execution plan (never executes code) |
| `reproduce run` | Execute reproduction commands |
| `reproduce status` | Show status of a run directory |
| `reproduce report` | Generate report from a run directory |
| `reproduce compare` | Compare run against expected values |
| `reproduce bundle` | Create evidence bundle ZIP |
| `reproduce inspect` | Inspect evidence bundle |
| `reproduce verify-bundle` | Verify bundle integrity |

## Quick start

```bash
# 1. Generate a plan
oss-paper-ci reproduce plan .

# 2. Execute with safety gates
oss-paper-ci reproduce run . --execute --sandbox local

# 3. Generate report
oss-paper-ci reproduce report .oss-paper-ci-repro-run --format html --output reproduction.html

# 4. Compare against expected
oss-paper-ci reproduce compare .oss-paper-ci-repro-run --expected reproducibility.yml

# 5. Create evidence bundle
oss-paper-ci reproduce bundle .oss-paper-ci-repro-run --output reproduction-evidence.zip
```

## reproducibility.yml schema v0.2

The orchestrator extends the existing `reproducibility.yml` schema with new sections:

```yaml
schema_version: "0.2"

environment:
  type: python
  python: ">=3.10"

commands:
  - id: train
    run: python scripts/train.py
    timeout_seconds: 60
    expected_artifacts:
      - results/model.json

  - id: evaluate
    run: python scripts/evaluate.py
    timeout_seconds: 60
    depends_on: [train]
    expected_artifacts:
      - results/metrics.json

artifacts:
  - path: results/metrics.json
    type: metrics

metrics:
  - file: results/metrics.json
    key: accuracy
    expected_min: 0.0
    expected_max: 1.0

safety:
  network: false
  allow_shell: false
  max_runtime_seconds: 300
  max_artifact_mb: 20
```

### Backward compatibility

Old-format `reproducibility.yml` files (without `schema_version` or `commands`) are automatically compatible. Experiments are converted to commands.

## Safety model

- **Dangerous command blocking:** Commands matching dangerous patterns (rm -rf, sudo, curl|bash, etc.) are blocked.
- **Timeout enforcement:** Each command has a configurable timeout.
- **Dependency ordering:** Commands execute in dependency order.
- **Path isolation:** Run directory is separate from the repository.
- **No absolute paths:** Reports use relative paths only.

## See also

- [reproduction-plan.md](reproduction-plan.md) — Plan generation
- [reproduction-run.md](reproduction-run.md) — Execution model
- [reproduction-artifacts.md](reproduction-artifacts.md) — Artifact validation
- [reproduction-metrics.md](reproduction-metrics.md) — Metric validation
- [reproduction-sandbox.md](reproduction-sandbox.md) — Sandbox isolation
- [reproduction-bundle.md](reproduction-bundle.md) — Evidence bundles
- [reproduction-safety.md](reproduction-safety.md) — Safety model
