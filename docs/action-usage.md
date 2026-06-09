# GitHub Action Usage

There are three ways to use oss-paper-ci in GitHub Actions.

## 1. Use the GitHub Action (recommended)

After oss-paper-ci is published with a tag (e.g. `v1.0.0rc1`):

```yaml
steps:
  - uses: actions/checkout@v4
  - uses: Akastella/oss-paper-ci@v1.0.0rc1
    with:
      path: "."
      format: "markdown"
      output: "report.md"
```

**Inputs:**

| Input | Description | Default |
|-------|-------------|---------|
| `path` | Path to repository root | `.` |
| `profile` | Policy profile: lenient, default, strict, publication | `default` |
| `config` | Path to config file | (auto-detect) |
| `contract` | Path to reproducibility.yml | (none) |
| `format` | Output format: json, markdown, sarif | `markdown` |
| `output` | Output file path | `oss-paper-ci-report.md` |
| `fail-under` | Minimum score threshold (0 = disabled) | `0` |
| `strict` | Fail on any warning | `false` |
| `baseline` | Path to baseline file | (none) |
| `fail-on-regression` | Fail if regression detected | `false` |
| `upload-sarif` | Upload SARIF to Code Scanning | `false` |
| `github-annotations` | Emit GitHub workflow annotations | `true` |
| `step-summary` | Write GitHub step summary | `true` |

## 2. Source checkout (before stable release)

Check out the tool repository and install from source:

```yaml
steps:
  - uses: actions/checkout@v4
  - uses: actions/setup-python@v5
    with:
      python-version: "3.12"
  - name: Checkout oss-paper-ci
    uses: actions/checkout@v4
    with:
      repository: Akastella/oss-paper-ci
      ref: v1.0.0rc1
      path: _tools/oss-paper-ci
  - name: Install
    run: python -m pip install ./_tools/oss-paper-ci
  - name: Run
    run: oss-paper-ci scan . --format markdown -o report.md
```

## 3. PyPI installation (after publication)

After oss-paper-ci is published to PyPI:

```yaml
steps:
  - uses: actions/setup-python@v5
    with:
      python-version: "3.12"
  - name: Install oss-paper-ci
    run: python -m pip install oss-paper-ci  # after PyPI publication
  - name: Run
    run: oss-paper-ci scan . --format markdown -o report.md
```

## Full example with SARIF and PR comments

See [examples/github-actions/demo-report.yml](../examples/github-actions/demo-report.yml)
for a complete workflow with SARIF upload and PR comments.
