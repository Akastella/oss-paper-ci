# Security Scan

The `oss-paper-ci security scan` command performs local static analysis for common security issues.

## Usage

```bash
oss-paper-ci security scan .
oss-paper-ci security scan . --format json
oss-paper-ci security scan . --format markdown
oss-paper-ci security scan . --output security-report.md
```

## What It Checks

### Secret Patterns

| Pattern | Severity | Description |
|---------|----------|-------------|
| OpenAI API Key | High | `sk-...T3BlbkFJ...` pattern |
| GitHub Token | High | `ghp_`, `gho_`, `ghu_`, `ghs_`, `ghr_` patterns |
| AWS Access Key | High | `AKIA...` pattern |
| Private Key Block | High | `-----BEGIN ... PRIVATE KEY-----` |
| Bearer Token | Medium | `Bearer ...` pattern |
| Generic API Key | Medium | `api_key=...` or `apikey: ...` patterns |

### Dangerous Shell Patterns

| Pattern | Severity | Description |
|---------|----------|-------------|
| curl pipe to bash | High | `curl ... \| bash` |
| wget pipe to shell | High | `wget ... \| sh` |
| Recursive force delete | High | `rm -rf /` |
| Sudo usage | Medium | `sudo` in CI |
| World-writable | Medium | `chmod 777` |
| Eval with variable | High | `eval $VAR` |
| Unsafe pickle | High | `pickle.load` |

### Environment Files

- `.env` files committed to the repository

## Redaction

Secret values are **always redacted** in the output:

```
sk-a...fJ35
```

The scanner shows only the first and last few characters. The full value is never displayed.

## Skipping Directories

The scanner skips:
- `.git/`
- `venv/`, `.venv/`
- `node_modules/`
- `target/`, `dist/`, `build/`, `site/`
- `__pycache__/`
- `.pytest_cache/`, `.mypy_cache/`
- `.egg-info/`

## Output Formats

- **Markdown**: Human-readable report
- **JSON**: Machine-readable with full finding details

## Limitations

- Pattern-based detection; may produce false positives
- Does not scan binary files or archives
- Does not detect all secret types
- Does not verify if detected secrets are real or fake
- Static analysis only; does not execute code

## See Also

- [trust.md](trust.md) — Trust & supply-chain security overview
- [SECURITY.md](../SECURITY.md) — Threat model and security policy
