# Maintainer Pack

The maintainer profile is designed for repository maintainers, CI administrators, and release managers.

## Usage

```bash
oss-paper-ci evidence . --profile maintainer --format json --output maintainer-report.json
```

## What the Maintainer Pack Provides

- **Workflow audit**: GitHub Actions permissions, triggers, action pinning
- **Dependency inventory**: Runtime and dev dependencies
- **Trust assessment**: Security findings, secret patterns
- **Provenance**: Build environment and artifact hashes
- **CI integration**: Recommendations for GitHub Action setup

## CI Integration

```yaml
# .github/workflows/evidence-report.yml
name: Evidence Report
on: [push, pull_request]
jobs:
  evidence:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v6
      - uses: actions/setup-python@v6
      - run: pip install oss-paper-ci  # after PyPI publication
      - run: oss-paper-ci evidence . --profile maintainer --format json --output evidence.json
      - uses: actions/upload-artifact@v4
        with:
          name: evidence-report
          path: evidence.json
```

## See Also

- [evidence-report.md](evidence-report.md) — Report structure
- [reviewer-pack.md](reviewer-pack.md) — Reviewer guidance
- [author-pack.md](author-pack.md) — Author guidance
