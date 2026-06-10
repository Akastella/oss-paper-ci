# Getting Started

## Install

```bash
# From source
git clone https://github.com/Akastella/oss-paper-ci.git
cd oss-paper-ci
pip install -e ".[dev]"

# Verify
oss-paper-ci version
```

See [Installation](installation.md) for more options.

## Scan a repository

```bash
oss-paper-ci scan /path/to/your/repo
```

This produces a scored Markdown report with findings and recommendations.

## Generate HTML report

```bash
oss-paper-ci scan . --format html --output report.html
```

## Use in GitHub Actions

```yaml
- uses: actions/checkout@v4
- uses: Akastella/oss-paper-ci@v1
  with:
    path: "."
    format: "markdown"
```

See [GitHub Actions Guide](github-action.md).

## Attempt reproduction

```bash
# Safe: dry-run shows what would happen
oss-paper-ci reproduce https://github.com/owner/paper-repo --dry-run

# Execute: actually run commands (requires trust)
oss-paper-ci reproduce https://github.com/owner/paper-repo \
  --execute --install --format html --output report.html
```

See [Reproduction](reproduce.md).

## Next steps

- [CLI Reference](cli-reference.md) — all commands
- [Configuration](configuration.md) — customize behavior
- [Policy Profiles](policy-profiles.md) — adjust strictness
- [Demo Gallery](demo-gallery.md) — see example outputs
