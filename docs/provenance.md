# Provenance Manifest

The `oss-paper-ci trust provenance` command generates a local provenance manifest.

## Usage

```bash
oss-paper-ci trust provenance .
oss-paper-ci trust provenance . --format json
oss-paper-ci trust provenance . --format markdown
oss-paper-ci trust provenance . --include-timestamp
oss-paper-ci trust provenance . --output provenance.json
```

## Manifest Structure

```json
{
  "schema_version": "0.1",
  "tool": "oss-paper-ci",
  "tool_version": "2.9.0rc1",
  "source": {
    "repo": "my-project",
    "commit": "abc123...",
    "dirty": false
  },
  "build": {
    "python_version": "3.12.0",
    "platform": "Linux x86_64"
  },
  "artifacts": [
    {
      "path": "release.zip",
      "sha256": "def456...",
      "size_bytes": 12345
    }
  ],
  "limitations": [
    "Local provenance manifest; not a signed attestation.",
    "Not SLSA compliant."
  ]
}
```

## Fields

### source

- `repo`: Repository name (relative, no absolute paths)
- `commit`: Git commit SHA (null if git not available)
- `dirty`: Whether the working directory has uncommitted changes (null if unknown)

### build

- `python_version`: Python version used
- `platform`: OS and architecture
- `timestamp_utc`: UTC timestamp (only with `--include-timestamp`)

### artifacts

List of artifacts with:
- `path`: Filename only (no absolute paths)
- `sha256`: SHA256 hash
- `size_bytes`: File size

## Stability

By default (without `--include-timestamp`), the manifest is deterministic and suitable for golden file testing.

## What It Does NOT Do

- **No cryptographic signing**: Not a signed attestation
- **No SLSA compliance**: Does not meet SLSA requirements
- **No external verification**: Does not verify third-party integrity
- **No absolute paths**: Never includes local filesystem paths

## See Also

- [trust.md](trust.md) — Trust & supply-chain security overview
- [release-verification.md](release-verification.md) — Artifact verification
