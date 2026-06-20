# Security Policy

## Supported versions

| Version | Supported          |
|---------|--------------------|
| 2.9.x   | :white_check_mark: |
| 2.0.x   | :white_check_mark: |
| 1.x     | :white_check_mark: |

## Reporting a vulnerability

If you discover a security vulnerability, please report it responsibly.

**Do not open a public GitHub issue for security vulnerabilities.**

Instead, email the maintainers at: security@oss-paper-ci.dev

Include:
- Description of the vulnerability
- Steps to reproduce
- Potential impact

We will acknowledge receipt within 48 hours and aim to provide a fix within 14 days.

## Scope & Threat Model

### Primary Use Case
oss-paper-ci is primarily a read-only static analysis tool for checking reproducibility readiness. In scan mode, it does not execute code or make network requests.

### Attack Surfaces

| Component | Risk | Mitigation |
|-----------|------|------------|
| YAML config | Malicious configs | `yaml.safe_load` |
| Path traversal | Malicious repo paths | `pathlib` resolution |
| `reproduce --execute` | Malicious scripts | Dangerous command blocklist, timeout, temp dir isolation (no sandbox) |
| GitHub Actions | Supply-chain attacks | Permissions audit, action pinning checks |
| Release artifacts | Tampering | SHA256SUMS verification |
| Secrets in code | Credential leakage | Pattern-based scanning (heuristic) |

### Security Scan Limitations

- **Not a security certification**: `oss-paper-ci security scan` is local static analysis only.
- **Heuristic detection**: Secret patterns may produce false positives or miss obfuscated secrets.
- **No sandboxing**: `reproduce --execute` runs commands in subprocess with shell=True; no container/chroot/seccomp.
- **No cryptographic signing**: Release artifacts use SHA256SUMS but no Sigstore/GPG signing.
- **No SBOM standard**: Dependency inventory is lightweight; not official SPDX/CycloneDX.
- **No external verification**: Does not check if GitHub Actions or dependencies are compromised.

### What We Do NOT Claim

- No SLSA compliance
- No Sigstore integration
- No official SPDX or CycloneDX SBOM
- No cryptographic verification of third-party dependencies
- No sandboxing of untrusted code execution
- No complete secret detection
