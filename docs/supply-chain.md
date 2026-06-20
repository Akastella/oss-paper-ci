# Supply-Chain Security

OSS-Paper-CI includes lightweight supply-chain security checks.

## Overview

| Check | Tool | What It Does |
|-------|------|--------------|
| Workflow audit | `trust audit` | Checks GitHub Actions permissions, triggers, action pinning |
| Secret scan | `security scan` | Detects common secret patterns in code |
| Dependency inventory | `trust inventory` | Lists declared dependencies (SBOM-like) |
| Provenance manifest | `trust provenance` | Records build environment and artifact hashes |
| Artifact verification | `trust verify-artifacts` | Verifies SHA256 checksums |

## What We Check

### GitHub Actions

- Permissions are explicitly declared (not inherited defaults)
- No `permissions: write-all`
- No `pull_request_target` with PR code checkout
- Official actions are major-version pinned
- Third-party actions are SHA-pinned

### Code

- No common secret patterns (API keys, tokens, private keys)
- No dangerous shell patterns (curl|bash, sudo, rm -rf)
- No `.env` files committed

### Dependencies

- Python dependencies are declared in pyproject.toml
- Docker base images are identified
- Lockfiles are detected

### Artifacts

- SHA256SUMS are generated for release artifacts
- Artifacts can be verified against checksums

## What We Do NOT Check

- **No vulnerability scanning**: Does not check for known CVEs
- **No dependency resolution**: Does not resolve transitive dependencies
- **No cryptographic signing**: No Sigstore, GPG, or similar
- **No SBOM standard**: Not official SPDX or CycloneDX
- **No external verification**: Does not verify if actions or packages are compromised
- **No sandboxing**: Does not execute untrusted code

## Limitations

These checks are **local static analysis only**:

- No network calls
- No external API verification
- Pattern-based detection may produce false positives
- Cannot detect all supply-chain attacks
- Not a security certification

## See Also

- [SECURITY.md](../SECURITY.md) — Threat model and security policy
- [trust.md](trust.md) — Trust commands overview
- [security-limitations.md](security-limitations.md) — Detailed limitations
