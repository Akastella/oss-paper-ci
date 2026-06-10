# Security Policy

## Supported versions

| Version | Supported          |
|---------|--------------------|
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

## Scope

oss-paper-ci is primarily a read-only static analysis tool. In scan mode, it does
not execute code or make network requests. The `reproduce --execute` command can
run code from repositories, but only when explicitly enabled. The attack surface
is limited to:

- Malicious YAML config files (mitigated by using `yaml.safe_load`)
- Path traversal in scanned repositories (mitigated by `pathlib` and resolved paths)
