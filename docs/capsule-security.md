# Capsule Security

## What Capsules Are

Capsules are **evidence packages** that record a reproduction attempt.
They contain reports, logs, metadata, and integrity checksums.

## What Capsules Are NOT

- Capsules are **NOT** proof that a paper is correct
- Capsules are **NOT** cryptographic signatures
- Capsules are **NOT** tamper-proof (SHA256 detects changes but doesn't prevent them)
- Capsules do **NOT** verify scientific claims

## Security Considerations

### Before Sharing

Capsules may contain:
- Full stdout/stderr logs from reproduction commands
- File paths (redacted but may still reveal structure)
- Environment details (Python version, packages)
- Generated artifacts

**Review capsule contents before sharing publicly.**

### Path Redaction

Absolute paths are redacted to `<redacted>/basename` in metadata.
Relative paths within the repository are preserved.

### Log Truncation

Logs are truncated at 1 MB per file. Sensitive information may
still be present in the first 1 MB.

### Artifact Limits

- Max 10 MB per artifact file
- Max 100 MB total capsule size
- Max 200 artifact files
- venv, .git, cache directories are excluded

### Verification Scope

`capsule verify` checks:
- Structural integrity (zip, manifest, required files)
- Hash integrity (SHA256 matches)
- Path safety (no traversal, no absolute paths)

It does NOT check:
- Whether the commands were appropriate
- Whether the environment was complete
- Whether the results are scientifically valid

## Recommendations

- Only use `--execute` on trusted repositories
- Review logs before sharing capsules
- Use capsules for archival, not as proof of correctness
- Combine with oss-paper-ci scan for reproducibility readiness
