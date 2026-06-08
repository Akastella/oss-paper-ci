# Security Policy

## Supported versions

| Version | Supported          |
|---------|--------------------|
| 0.1.x   | :white_check_mark: |

## Reporting a vulnerability

If you discover a security vulnerability, please report it responsibly.

**Do not open a public GitHub issue for security vulnerabilities.**

Instead, email the maintainers at: security@oss-paper-ci.dev

Include:
- Description of the vulnerability
- Steps to reproduce
- Potential impact

We will acknowledge receipt within 48 hours and aim to provide a fix within 14 days.

## Scope

oss-paper-ci is a read-only static analysis tool. It does not execute code in the
scanned repository, make network requests, or modify files outside its own report
output. The attack surface is limited to:

- Malicious YAML config files (mitigated by using `yaml.safe_load`)
- Path traversal in scanned repositories (mitigated by `pathlib` and resolved paths)
