# Reproduction Capsules

A reproduction capsule is a self-contained, verifiable package that records
a reproduction attempt. It includes the manifest, reports, logs, metadata,
and SHA256 integrity checksums.

## Quick Start

```bash
# Generate a capsule during reproduction
oss-paper-ci reproduce https://github.com/owner/paper-repo \
  --execute --install --capsule repro-capsule.zip

# Verify capsule integrity
oss-paper-ci capsule verify repro-capsule.zip

# Inspect capsule contents
oss-paper-ci capsule inspect repro-capsule.zip

# Compare two capsules
oss-paper-ci capsule diff old-capsule.zip new-capsule.zip
```

## What's in a Capsule

```
oss-paper-ci-capsule/
  capsule.json          # Manifest with schema, source, execution, reports
  SHA256SUMS            # Integrity checksums for all files
  reports/
    reproduce_report.json/md/html
    scan_report.json/md
  logs/
    install_000.stdout.txt/stderr.txt
    command_000.stdout.txt/stderr.txt
  artifacts/
    artifact_index.json
    generated/          # Files generated during reproduction
  metadata/
    source.json         # Repository and commit info
    environment.json    # Detected environment files
    commands.json       # Command plan and results
    oss_paper_ci.json   # Tool version and platform
    limitations.md      # What this capsule does NOT prove
```

## Capsule vs Report

A **report** is a single document (Markdown, JSON, or HTML) describing
a reproduction attempt. A **capsule** is a verifiable archive containing
the report plus all supporting evidence: logs, metadata, artifacts, and
integrity checksums.

Use reports for quick viewing. Use capsules for archiving, sharing, and
verification.

## See Also

- [Capsule Format](capsule-format.md) — detailed format specification
- [Capsule Verify](capsule-verify.md) — verification details
- [Capsule Security](capsule-security.md) — security considerations
