# Trust & Supply-Chain Security Examples

This directory contains example outputs from the trust and security commands.

## Files

- `trust_report.json` — Trust audit report (JSON)
- `trust_report.md` — Trust audit report (Markdown)
- `security_scan.json` — Security scan results (JSON)
- `security_scan.md` — Security scan results (Markdown)
- `dependency_inventory.json` — Dependency inventory (JSON)
- `dependency_inventory.md` — Dependency inventory (Markdown)
- `provenance.json` — Provenance manifest
- `release_verification.md` — Artifact verification report

## Generating These Examples

These files were generated using the following commands:

```bash
# Trust audit
oss-paper-ci trust audit . --format json --output examples/trust/trust_report.json
oss-paper-ci trust audit . --format markdown --output examples/trust/trust_report.md

# Security scan (using test fixture with fake secrets)
oss-paper-ci security scan tests/fixtures/security_secret_repo --format json --output examples/trust/security_scan.json
oss-paper-ci security scan tests/fixtures/security_secret_repo --format markdown --output examples/trust/security_scan.md

# Dependency inventory
oss-paper-ci trust inventory . --format json --output examples/trust/dependency_inventory.json
oss-paper-ci trust inventory . --format markdown --output examples/trust/dependency_inventory.md

# Provenance manifest
oss-paper-ci trust provenance . --format json --output examples/trust/provenance.json

# Artifact verification
oss-paper-ci trust verify-artifacts tests/fixtures/trust_release_artifacts --format markdown --output examples/trust/release_verification.md
```

## Limitations

- All checks are local static analysis only
- No external APIs or services are called
- Secret detection is heuristic (may produce false positives/negatives)
- Not a security certification
