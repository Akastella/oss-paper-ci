# Capsule Verification

The `capsule verify` command checks a capsule's structural integrity
and SHA256 hash consistency.

## What It Checks

1. **Zip structure**: file can be opened as a valid zip
2. **Root directory**: top-level dir is `oss-paper-ci-capsule/`
3. **Manifest**: `capsule.json` exists and is valid JSON
4. **Schema version**: recognized schema version
5. **SHA256SUMS**: file exists
6. **Hash integrity**: all hashes match their files
7. **Path safety**: no path traversal or absolute paths
8. **Required files**: recommended files are present

## What It Does NOT Check

- Scientific correctness of the reproduction
- Whether the paper's claims are valid
- Whether the code produces correct results
- Whether the environment is complete

## Usage

```bash
# Text output (default)
oss-paper-ci capsule verify capsule.zip

# JSON output
oss-paper-ci capsule verify capsule.zip --format json

# Markdown output
oss-paper-ci capsule verify capsule.zip --format markdown --output verify.md
```

## Exit Codes

- `0`: verification passed
- `1`: verification failed (errors found)

## Example Output

```
Capsule verification: PASSED
- Schema: 0.1
- Files checked: 12
- Hashes matched: 12
- Warnings: 0
```

## Tamper Detection

If any file in the capsule has been modified after creation, the
SHA256 hash will not match and verification will fail. This provides
a basic integrity check but is not cryptographic signing.
