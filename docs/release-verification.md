# Release Verification

The `oss-paper-ci trust verify-artifacts` command verifies release artifacts against SHA256SUMS.

## Usage

```bash
oss-paper-ci trust verify-artifacts release-artifacts/
oss-paper-ci trust verify-artifacts release-artifacts/ --checksums SHA256SUMS
oss-paper-ci trust verify-artifacts release-artifacts/ --format json
oss-paper-ci trust verify-artifacts release-artifacts/ --output verification.md
```

## How It Works

1. Finds `SHA256SUMS` or `SHA256SUMS.txt` in the artifact directory
2. Parses expected hashes
3. Computes actual SHA256 for each listed artifact
4. Reports verified, failed, and missing artifacts

## Example Output

```
# Artifact Verification Report

**Status:** PASS

## Verified
- ✅ `oss-paper-ci-v2.9.0rc1-github-clean.zip`
- ✅ `oss_paper_ci-2.9.0rc1-py3-none-any.whl`

## Failed
- ❌ `tampered.zip` (expected `abc123...`, got `def456...`)

## Missing
- ⚠️ `nonexistent.zip`
```

## SHA256SUMS Format

Standard SHA256SUMS format:

```
<hash>  <filename>
<hash>  <filename>
```

The checksums file itself is excluded from verification.

## Exit Code

- `0`: All artifacts verified
- `1`: Verification failed (tampered or missing artifacts)

## See Also

- [trust.md](trust.md) — Trust & supply-chain security overview
- [provenance.md](provenance.md) — Provenance manifest
