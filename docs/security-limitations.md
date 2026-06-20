# Security Limitations

This document describes what the security and trust checks can and cannot do.

## What We Can Do

| Capability | Description |
|------------|-------------|
| Pattern-based secret detection | Detect common secret formats (OpenAI, GitHub, AWS, etc.) |
| Dangerous command detection | Flag shell commands that could damage the system |
| Workflow permission audit | Check GitHub Actions for overly broad permissions |
| Action pinning check | Verify actions are pinned to versions or SHAs |
| Dependency listing | List declared dependencies |
| SHA256 verification | Verify artifact integrity via checksums |
| Docker base image detection | Identify Docker base images |

## What We Cannot Do

| Limitation | Why |
|------------|-----|
| Detect all secrets | Pattern-based; obfuscated or unusual formats are missed |
| Verify third-party integrity | No network calls; cannot check if packages are compromised |
| Sandbox execution | No container/chroot/seccomp for `reproduce --execute` |
| Cryptographic signing | No Sigstore, GPG, or similar integration |
| Official SBOM | Not SPDX or CycloneDX compliant |
| Vulnerability scanning | No CVE database checking |
| Runtime analysis | Static analysis only; cannot detect runtime issues |

## False Positives

The scanner may flag:
- Fake secrets in test files
- Example API keys in documentation
- Placeholder tokens in configuration templates

These can be suppressed or ignored when confirmed as false positives.

## False Negatives

The scanner may miss:
- Secrets that don't match common patterns
- Obfuscated or encoded secrets
- Secrets in binary files
- Secrets in archives or compressed files
- Unusual secret formats

## Recommendations

1. **Use as a first pass**: These checks catch obvious issues but are not comprehensive
2. **Combine with other tools**: Use dedicated secret scanners, SAST tools, and dependency scanners
3. **Review findings manually**: Not all findings are real issues
4. **Don't rely solely on this**: This is not a security certification

## See Also

- [SECURITY.md](../SECURITY.md) — Threat model and security policy
- [trust.md](trust.md) — Trust commands overview
- [supply-chain.md](supply-chain.md) — Supply-chain considerations
