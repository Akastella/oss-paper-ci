# Author Pack

The author profile is designed for paper authors who want to improve their repository's reproducibility.

## Usage

```bash
oss-paper-ci evidence . --profile author --format markdown --output author-report.md
```

## What the Author Pack Provides

- **Current score**: How your repository ranks on reproducibility readiness
- **Missing items**: What documentation and artifacts are absent
- **Recommended next steps**: Prioritized actions to improve your score
- **Adoption suggestions**: Specific files to add or modify
- **Commands to run**: Exact commands to verify improvements

## Example Next Steps

1. Add `reproducibility.yml` with execution instructions
2. Add `data/README.md` documenting your datasets
3. Add `requirements.txt` or `pyproject.toml` with pinned dependencies
4. Run `oss-paper-ci scan . --verbose` for detailed recommendations

## Improving Your Score

```bash
# See what's missing
oss-paper-ci evidence . --profile author

# Get scaffold suggestions
oss-paper-ci scaffold .

# Preview fixes without applying
oss-paper-ci fix preview .

# Apply safe fixes
oss-paper-ci fix apply . --yes
```

## See Also

- [evidence-report.md](evidence-report.md) — Report structure
- [reviewer-pack.md](reviewer-pack.md) — Reviewer guidance
- [maintainer-pack.md](maintainer-pack.md) — Maintainer guidance
