# GitHub Actions Integration

## Quick start (recommended)

The recommended way to use oss-paper-ci is via the GitHub Action. After
oss-paper-ci is published to GitHub with a tag (e.g. `v1`), add this as
`.github/workflows/reproducibility.yml` in your scientific repository:

```yaml
name: Reproducibility Check

on:
  pull_request:
  push:
    branches: [main]

jobs:
  oss-paper-ci:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - uses: Akastella/oss-paper-ci@v1
        with:
          path: "."
          format: "markdown"
          output: "report.md"

      - name: Upload report
        if: always()
        uses: actions/upload-artifact@v4
        with:
          name: reproducibility-report
          path: report.md
```

Replace `Akastella/oss-paper-ci` with the actual GitHub repository after publication.

## Source checkout (before Action/PyPI publication)

If the GitHub Action or PyPI package is not yet available, you can install
from source by checking out the tool repository:

```yaml
name: Reproducibility Check

on:
  pull_request:
  push:
    branches: [main]

jobs:
  check:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - uses: actions/setup-python@v5
        with:
          python-version: "3.12"

      - name: Checkout oss-paper-ci source
        uses: actions/checkout@v4
        with:
          repository: Akastella/oss-paper-ci
          ref: v1.0.0rc1
          path: _tools/oss-paper-ci

      - name: Install oss-paper-ci
        run: python -m pip install ./_tools/oss-paper-ci

      - name: Run scan
        run: oss-paper-ci scan . --format markdown -o report.md

      - name: Upload report
        if: always()
        uses: actions/upload-artifact@v4
        with:
          name: reproducibility-report
          path: report.md
```

## PyPI installation (after publication)

After oss-paper-ci is published to PyPI, you can install directly:

```yaml
- uses: actions/setup-python@v5
  with:
    python-version: "3.12"

- name: Install oss-paper-ci (after PyPI publication)
  run: python -m pip install oss-paper-ci  # after PyPI publication
```

## Using SARIF with GitHub Code Scanning

Upload SARIF output to GitHub Code Scanning to see reproducibility results in
the repository's Security tab.

```yaml
name: Reproducibility Scan (SARIF)

on:
  push:
    branches: [main]
  pull_request:

jobs:
  scan:
    runs-on: ubuntu-latest
    permissions:
      security-events: write
    steps:
      - uses: actions/checkout@v4

      - uses: Akastella/oss-paper-ci@v1
        with:
          path: "."
          format: "sarif"
          output: "results.sarif"

      - name: Upload SARIF to GitHub
        uses: github/codeql-action/upload-sarif@v3
        with:
          sarif_file: results.sarif
```

After upload, results appear at **Security > Code scanning** in the repository.

See [docs/sarif.md](sarif.md) for SARIF format details.

## Posting report as a PR comment

```yaml
name: Reproducibility Check

on:
  pull_request:

jobs:
  reproducibility:
    runs-on: ubuntu-latest
    permissions:
      pull-requests: write
    steps:
      - uses: actions/checkout@v4

      - uses: Akastella/oss-paper-ci@v1
        with:
          path: "."
          format: "markdown"
          output: "report.md"

      - name: Post PR comment
        if: github.event_name == 'pull_request'
        uses: actions/github-script@v7
        with:
          script: |
            const fs = require('fs');
            const report = fs.readFileSync('report.md', 'utf8');
            const body = `## Reproducibility Report\n\n${report}`;
            const { data: comments } = await github.rest.issues.listComments({
              owner: context.repo.owner,
              repo: context.repo.repo,
              issue_number: context.issue.number,
            });
            const existing = comments.find(c =>
              c.user.type === 'Bot' && c.body.includes('Reproducibility Report')
            );
            if (existing) {
              await github.rest.issues.updateComment({
                owner: context.repo.owner,
                repo: context.repo.repo,
                comment_id: existing.id,
                body,
              });
            } else {
              await github.rest.issues.createComment({
                owner: context.repo.owner,
                repo: context.repo.repo,
                issue_number: context.issue.number,
                body,
              });
            }

      - name: Upload report
        if: always()
        uses: actions/upload-artifact@v4
        with:
          name: reproducibility-report
          path: report.md
```

## Interpreting exit codes in CI

| Exit code | CI result | Meaning                                    |
|-----------|-----------|--------------------------------------------|
| 0         | Success   | All checks passed                          |
| 1         | Success   | Warnings present, no hard failures         |
| 2         | Failure   | At least one error-level check failed      |

## Periodic scan workflow

Run a scan on a schedule to catch regressions:

```yaml
name: Weekly Reproducibility Audit

on:
  schedule:
    - cron: "23 8 * * 1"  # Monday at 08:23 UTC
  workflow_dispatch: {}

jobs:
  audit:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - uses: Akastella/oss-paper-ci@v1
        with:
          path: "."
          format: "json"
          output: "report.json"

      - name: Upload JSON report
        uses: actions/upload-artifact@v4
        with:
          name: reproducibility-audit
          path: report.json
```
