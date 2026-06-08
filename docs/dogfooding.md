# Dogfooding

oss-paper-ci tests itself by scanning its own repository and test fixtures.

## What is dogfooding

Dogfooding means using your own tool on your own project. For oss-paper-ci,
this means:

1. The CI pipeline runs `oss-paper-ci scan .` on the oss-paper-ci repo itself.
2. Test fixtures represent different repository states (good, bad, realistic).
3. The tool's own score and checks are visible in CI output.

## How we test on ourselves

### CI self-scan

The CI workflow (`.github/workflows/ci.yml`) includes a self-scan step:

```yaml
- name: Self-scan
  run: python -m oss_paper_ci scan . --format json
```

This runs after tests pass. It verifies that:

- The tool does not crash on its own codebase.
- The JSON output is valid.
- No regressions in the scanning logic.

### Test fixtures

The `tests/fixtures/` directory contains purpose-built repositories:

| Fixture              | Purpose                                           |
|----------------------|---------------------------------------------------|
| `paper_ready_repo`   | A well-structured repo that should score high.    |
| `broken_paper_repo`  | A repo with known issues that should score low.   |
| `realistic_ml_repo`  | A realistic ML project with configs and notebooks.|
| `minimal_bad_repo`   | A minimal repo missing most basics.               |

Each fixture is a real directory structure (not mocked). Tests scan these
fixtures and assert on specific check results, scores, and statuses.

### Fixture scoring expectations

| Fixture              | Expected score range | Expected status |
|----------------------|----------------------|-----------------|
| `paper_ready_repo`   | 70-95                | pass or warn    |
| `broken_paper_repo`  | 20-50                | fail            |
| `realistic_ml_repo`  | 75-100               | pass or warn    |
| `minimal_bad_repo`   | 0-30                 | fail            |

These ranges are validated in `tests/test_scanner.py`.

## Results from scanning oss-paper-ci

When oss-paper-ci scans itself, it checks for:

- README.md (present)
- LICENSE (present)
- CITATION.cff (not present -- acceptable for a tool, not a paper)
- requirements.txt / pyproject.toml (present)
- Tests directory (present)
- CI workflows (present)
- Contributing guidelines (not present)

The self-scan is not expected to score 100/100. The tool is a CI utility, not
a scientific paper repository. The point is to verify the tool works, not to
achieve a high score on a non-paper project.

## How to scan your own repos

### Basic scan

```bash
cd /path/to/your/repo
oss-paper-ci scan
```

### Compare before and after

```bash
# Before changes
oss-paper-ci scan --format json -o before.json

# Make improvements (add README, LICENSE, etc.)

# After changes
oss-paper-ci scan --format json -o after.json

# Compare scores
python -c "
import json
with open('before.json') as f: b = json.load(f)
with open('after.json') as f: a = json.load(f)
print(f'Before: {b[\"summary\"][\"score\"]}')
print(f'After:  {a[\"summary\"][\"score\"]}')
"
```

### Track score over time

Store scan results in CI artifacts and plot the score over time to see whether
reproducibility readiness is improving or regressing.

## Adding new test fixtures

To add a fixture for a new test scenario:

1. Create a directory under `tests/fixtures/` with the desired file structure.
2. Add a test in `tests/test_scanner.py` that scans the fixture.
3. Assert on specific check results, score range, and status.

Keep fixtures minimal -- include only the files relevant to the test case.
