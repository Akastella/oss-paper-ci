# Release Process

## Pre-release checklist

1. Update version in `src/oss_paper_ci/__init__.py`
2. Update version in `pyproject.toml`
3. Update `CHANGELOG.md` with release notes
4. Update version references in test files
5. Run `python -m pytest` — all tests must pass
6. Run `python scripts/check_docs_truthfulness.py --check` — must pass
7. Run `python -m build` — must succeed
8. Run `python -m twine check dist/*` — must pass
9. Run `python scripts/make_release_package.py --version X.Y.Z`
10. Run `python scripts/verify_clean_package.py --zip release-artifacts/oss-paper-ci-vX.Y.Z-github-clean.zip`
11. Run `python scripts/release_gate.py` — must pass

## Tag and release

```bash
git tag vX.Y.Z
git push origin vX.Y.Z
```

The `release.yml` workflow will create a GitHub release.

## After release

1. Verify the GitHub release was created
2. Verify the clean package ZIP is attached
3. Test installation from the clean package

## Version scheme

- `X.Y.ZrcN` for release candidates
- `X.Y.Z` for stable releases
- Follow semantic versioning

## Scripts

| Script | Purpose |
|--------|---------|
| `scripts/make_release_package.py` | Build clean ZIP |
| `scripts/verify_clean_package.py` | Verify clean package |
| `scripts/release_gate.py` | Pre-release validation |
| `scripts/check_docs_truthfulness.py` | Documentation accuracy |
