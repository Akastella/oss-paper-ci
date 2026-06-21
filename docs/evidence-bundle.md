# Evidence Bundle

The `oss-paper-ci evidence bundle` command creates a shareable ZIP package containing the evidence report in multiple formats, a manifest, and SHA256 checksums.

## Usage

```bash
# Create a bundle
oss-paper-ci evidence bundle . --output evidence-bundle.zip

# Create with specific profile
oss-paper-ci evidence bundle . --profile author --output author-bundle.zip

# Inspect a bundle
oss-paper-ci evidence inspect evidence-bundle.zip

# Verify bundle integrity
oss-paper-ci evidence verify evidence-bundle.zip
```

## Bundle Contents

```
evidence-bundle/
  evidence-report.json     # Machine-readable report
  evidence-report.md       # Human-readable report
  evidence-report.html     # Self-contained HTML report
  limitations.md           # Detailed limitations
  manifest.json            # Bundle metadata and file hashes
  SHA256SUMS               # Checksums for verification
```

## Manifest

The `manifest.json` contains:
- Tool version
- Profile used
- Included sections
- File list with SHA256 hashes
- Limitations

## Verification

```bash
oss-paper-ci evidence verify evidence-bundle.zip
```

This checks:
- All files listed in SHA256SUMS are present
- All file hashes match
- No forbidden content (`.git/`, `venv/`, etc.)

## What the Bundle Does NOT Contain

- User data files or experiment artifacts
- `.git/` directory
- Virtual environments or caches
- Large binary files
- Local absolute paths
- Secrets or credentials

## Limitations

- The bundle is locally generated; not a signed attestation
- Does not verify third-party dependency integrity
- SHA256 checksums verify integrity, not authenticity
- Not SLSA, Sigstore, or Sigstore compliant

## See Also

- [evidence-report.md](evidence-report.md) — Report structure
- [evidence-limitations.md](evidence-limitations.md) — Detailed limitations
