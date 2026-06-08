# Release Checklist

Steps to follow when releasing a new version of oss-paper-ci.

## Pre-release

1. **Version bump**
   - Update `version` in `src/oss_paper_ci/__init__.py`.
   - Update `version` in `pyproject.toml`.
   - Ensure both match.

2. **CHANGELOG update**
   - Add a new section in `CHANGELOG.md` for the release.
   - List all changes under `Added`, `Changed`, `Fixed`, `Removed`.
   - Include the date.

3. **Run tests**
   ```bash
   python -m pytest tests/ -v
   ```
   All tests must pass.

4. **Self-scan clean**
   ```bash
   python -m oss_paper_ci scan . --format json
   ```
   Verify no crashes, valid JSON output.

5. **Dogfooding**
   - Scan test fixtures and verify expected scores.
   - Run on a real scientific repository to check for regressions.

6. **Documentation check**
   - Verify all docs in `docs/` are up to date.
   - Verify CLI examples in README still work.
   - Verify configuration reference matches actual config fields.

## Release

7. **Tag the release**
   ```bash
   git tag v<X.Y.Z>
   git push origin v<X.Y.Z>
   ```

8. **Verify CI passes**
   - All tests pass on the tag.
   - Self-scan succeeds.

## Post-release

9. **PyPI build (future)**
   When the project is published to PyPI:
   ```bash
   python -m build
   twine check dist/*
   twine upload dist/*
   ```

10. **Update pre-commit hook rev**
    Update `examples/pre-commit/.pre-commit-config.yaml` to reference the
    new tag.

11. **Verify installation**
    ```bash
    pip install -e ".[dev]"
    oss-paper-ci version
    ```

## Version numbering

oss-paper-ci follows [Semantic Versioning](https://semver.org/):

- **Major (X.0.0):** Breaking changes to CLI interface, config format, or
  report schema.
- **Minor (0.X.0):** New checks, new output formats, new features. Backward
  compatible.
- **Patch (0.0.X):** Bug fixes, documentation updates. Backward compatible.
