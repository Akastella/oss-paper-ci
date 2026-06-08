# Baselines

Baselines let you snapshot the current reproducibility score and check results
of a repository, then compare future scans against that snapshot to detect
regressions and improvements.  Baselines work without git -- they are plain
JSON files you commit, archive, or share.

## Quick start

```bash
# Create a baseline from the current state of a repo.
oss-paper-ci baseline create ./my-paper-repo -o .oss-paper-ci/baseline.json

# Later, compare the current state against that baseline.
oss-paper-ci baseline compare ./my-paper-repo --baseline .oss-paper-ci/baseline.json

# Fail CI if anything regressed.
oss-paper-ci baseline compare ./my-paper-repo \
    --baseline .oss-paper-ci/baseline.json \
    --fail-on-regression
```

## Creating a baseline

```bash
oss-paper-ci baseline create [PATH] [--output FILE]
```

- `PATH` defaults to `.` (current directory).
- `--output` / `-o` sets the destination file (default:
  `.oss-paper-ci/baseline.json`).

The command runs a full scan and writes a JSON file containing:

| Field             | Description                                |
|-------------------|--------------------------------------------|
| `schema_version`  | Always `"0.3"`                             |
| `created_at`      | ISO-8601 UTC timestamp                     |
| `repo_path`       | Absolute path that was scanned             |
| `score`           | Aggregate reproducibility score (0-100)    |
| `status`          | Overall status: `pass`, `warn`, or `fail`  |
| `check_results`   | Per-check id, title, severity, status, message |

## Comparing against a baseline

```bash
oss-paper-ci baseline compare [PATH] --baseline FILE [OPTIONS]
```

| Option               | Description                                     |
|----------------------|-------------------------------------------------|
| `--baseline FILE`    | Path to the baseline JSON (required)            |
| `--format FORMAT`    | `markdown` (default) or `json`                  |
| `--output FILE`      | Write report to file instead of stdout          |
| `--fail-on-regression` | Exit with code 1 if any regressions detected  |

### What the comparison reports

The comparison output includes:

- **score_delta** -- positive means improvement, negative means regression.
- **status_delta** -- e.g. `pass -> warn`.
- **regressions** -- checks that appeared for the first time and didn't pass.
- **new_findings** -- checks whose status worsened (e.g. `pass -> warn`).
- **improvements** -- checks that changed from `fail` to `pass`.
- **resolved_findings** -- checks that improved (but not to `pass`).

## Typical CI workflow

```yaml
# .github/workflows/reproducibility.yml
- name: Compare against baseline
  run: |
    oss-paper-ci baseline compare . \
        --baseline .oss-paper-ci/baseline.json \
        --fail-on-regression \
        --format markdown
```

## Updating a baseline

Re-run `baseline create` with the same `--output` path to overwrite the
previous baseline.  Commit the updated file to version control so the team
shares a single reference point.

## File format

Baseline files are valid JSON and can be inspected with any text editor or
`jq`:

```bash
jq '.score, .status, (.check_results | length)' .oss-paper-ci/baseline.json
```
