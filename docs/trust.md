# Trust & Supply-Chain Security

OSS-Paper-CI includes local static checks for supply-chain trust and security.

## Commands

### Trust Audit

```bash
oss-paper-ci trust audit .
oss-paper-ci trust audit . --format json
oss-paper-ci trust audit . --format markdown
oss-paper-ci trust audit . --format html
oss-paper-ci trust audit . --output trust-report.md
```

Aggregates workflow audit, security scan, dependency inventory, and provenance manifest into a single report.

### Security Scan

```bash
oss-paper-ci security scan .
oss-paper-ci security scan . --format json
oss-paper-ci security scan . --format markdown
oss-paper-ci security scan . --output security-report.md
```

Scans for:
- Secret patterns (OpenAI, GitHub, AWS, private keys, bearer tokens)
- Dangerous shell patterns (curl|bash, sudo, chmod 777, eval with variable, unsafe pickle)
- `.env` files committed to the repository

### Dependency Inventory

```bash
oss-paper-ci trust inventory .
oss-paper-ci trust inventory . --format json
oss-paper-ci trust inventory . --format markdown
oss-paper-ci trust inventory . --output inventory.json
```

Generates an SBOM-like inventory including:
- Python package metadata from pyproject.toml
- Runtime and dev dependencies
- GitHub Actions used
- Docker base images
- Detected lockfiles
- License information

### Provenance Manifest

```bash
oss-paper-ci trust provenance .
oss-paper-ci trust provenance . --format json
oss-paper-ci trust provenance . --format markdown
oss-paper-ci trust provenance . --output provenance.json
oss-paper-ci trust provenance . --include-timestamp
```

Generates a local provenance manifest with:
- Tool version
- Source commit (if git available)
- Python version and platform
- Artifact SHA256 hashes

### Artifact Verification

```bash
oss-paper-ci trust verify-artifacts release-artifacts/
oss-paper-ci trust verify-artifacts release-artifacts/ --checksums SHA256SUMS
oss-paper-ci trust verify-artifacts release-artifacts/ --format json
oss-paper-ci trust verify-artifacts release-artifacts/ --output verification.md
```

Verifies artifacts against SHA256SUMS file.

## What These Checks Do

| Check | What It Does | What It Does NOT Do |
|-------|--------------|---------------------|
| Workflow audit | Checks permissions, triggers, action pinning | Verify action integrity |
| Secret scan | Pattern-matches common secret formats | Detect all secrets or obfuscated keys |
| Dependency inventory | Lists declared dependencies | Resolve transitive dependencies |
| Provenance | Records build environment | Cryptographic signing |
| Artifact verification | Verifies SHA256 checksums | Verify artifact authenticity |

## Limitations

- **Local static analysis only**: No network calls, no external verification
- **Heuristic detection**: May produce false positives or miss obfuscated patterns
- **No cryptographic signing**: No Sigstore, GPG, or similar
- **No SBOM standard**: Not official SPDX or CycloneDX
- **No sandboxing**: Does not execute code; read-only analysis

## See Also

- [SECURITY.md](../SECURITY.md) — Threat model and security policy
- [security-scan.md](security-scan.md) — Security scan details
- [supply-chain.md](supply-chain.md) — Supply-chain considerations
- [workflow-audit.md](workflow-audit.md) — Workflow audit details
