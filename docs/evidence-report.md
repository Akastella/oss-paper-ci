# Unified Evidence Report

The `oss-paper-ci evidence` command generates a unified evidence report that aggregates all reproducibility, data, results, trust, and security information into a single shareable document.

## Usage

```bash
# Generate a reviewer-focused evidence report
oss-paper-ci evidence . --profile reviewer

# Generate an author-focused report
oss-paper-ci evidence . --profile author

# Generate a maintainer-focused report
oss-paper-ci evidence . --profile maintainer

# Output formats
oss-paper-ci evidence . --format markdown
oss-paper-ci evidence . --format json
oss-paper-ci evidence . --format html --output evidence.html

# Include specific sections only
oss-paper-ci evidence . --include reproducibility --include trust
```

## Profiles

### Reviewer Profile
- Emphasizes "what evidence is available to review"
- Uses neutral language
- Does not provide acceptance recommendations
- Does not judge scientific correctness
- Focus: environment, data, results, trust/security, limitations

### Author Profile
- Emphasizes "what to fix next"
- Includes adoption/scaffold suggestions
- Provides actionable next steps
- Focus: missing files, failing checks, recommendations

### Maintainer Profile
- Emphasizes CI, release, workflow, security, dependencies
- Includes GitHub Action integration suggestions
- Focus: workflow audit, provenance, dependency inventory

## Sections

| Section | Description |
|---------|-------------|
| `repository` | Git commit, detected ecosystems |
| `reproducibility` | Scan score, checks, findings |
| `data` | Data documentation and availability |
| `results` | Result artifact validation |
| `ecosystems` | Detected language ecosystems |
| `trust` | Trust audit, security scan, workflow audit |
| `adoption` | Missing files, recommended actions |

## What This Report Does NOT Do

- Does not prove scientific correctness
- Does not predict paper acceptance
- Does not replace human review
- Does not execute experiments (unless explicitly requested)
- Does not guarantee reproducibility

## See Also

- [evidence-bundle.md](evidence-bundle.md) — Shareable evidence bundles
- [reviewer-pack.md](reviewer-pack.md) — Reviewer-specific guidance
- [author-pack.md](author-pack.md) — Author-specific guidance
- [maintainer-pack.md](maintainer-pack.md) — Maintainer-specific guidance
- [evidence-schema.md](evidence-schema.md) — JSON schema reference
- [evidence-limitations.md](evidence-limitations.md) — Detailed limitations
