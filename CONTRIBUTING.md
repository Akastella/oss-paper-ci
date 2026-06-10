# Contributing to oss-paper-ci

## Development setup

```bash
git clone https://github.com/<owner>/<repo>.git
cd oss-paper-ci
pip install -e ".[dev]"
```

## Running tests

```bash
pytest
pytest --cov=oss_paper_ci          # with coverage
pytest -k test_meta                 # run a subset
```

## Project structure

```
src/oss_paper_ci/
  cli.py           # CLI entry point
  config.py        # Configuration loading
  models.py        # Data models (CheckResult, Report, etc.)
  scanner.py       # Orchestrates checks
  scoring.py       # Score calculation
  checks/          # All check implementations
    base.py        # BaseChecker and CheckContext
    metadata.py    # META001-META007
    environment.py # ENV001-ENV006
    experiments.py # EXP001-EXP006
    data.py        # DATA001-DATA006
    results.py     # RES001-RES005
    paper_code.py  # PAP001-PAP005
    ci.py          # CI001-CI006
  reporting/       # Output formatters
    json_report.py
    markdown_report.py
  utils/           # Filesystem and text helpers
tests/
  fixtures/        # Sample repos for testing
```

## Adding a new check

1. Choose the right module in `src/oss_paper_ci/checks/`.
2. Create a class that inherits from `BaseChecker`.
3. Set `check_id`, `title`, and `severity`.
4. Implement the `check(self, ctx: CheckContext) -> list[CheckResult]` method.
5. Decorate with `@register`.
6. Add tests in `tests/`.

Example:

```python
@register
class MyNewCheck(BaseChecker):
    check_id = "ENV007"
    title = "My new check"
    severity = Severity.WARNING

    def check(self, ctx: CheckContext) -> list[CheckResult]:
        if some_condition:
            return [self._pass("All good.")]
        return [self._warn("Something missing.", recommendation="Fix it.")]
```

## Submitting changes

1. Fork the repository.
2. Create a branch: `git checkout -b my-feature`
3. Make your changes and add tests.
4. Run `python -m pytest` and ensure all tests pass.
5. Run `python scripts/check_docs_truthfulness.py --check` — must pass.
6. Open a pull request against `main`.

## Code style

- Follow existing patterns in the codebase.
- Keep checkers focused: one concern per checker.
- Include `evidence` in every CheckResult.
- Write actionable `recommendation` strings.
