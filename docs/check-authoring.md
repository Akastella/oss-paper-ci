# Check Authoring Guide

How to write a new checker for oss-paper-ci.

## Overview

Each checker is a Python class that subclasses `BaseChecker`, is decorated with
`@register`, and implements a single `check()` method. The registry discovers
checkers automatically -- no configuration file needs updating.

## Step 1: Choose a module

Checkers live in `src/oss_paper_ci/checks/`. Each module covers one category:

| Module          | Category | Prefix |
|-----------------|----------|--------|
| `metadata.py`   | META     | META   |
| `environment.py`| ENV      | ENV    |
| `experiments.py`| EXP      | EXP    |
| `data.py`       | DATA     | DATA   |
| `results.py`    | RES      | RES    |
| `paper_code.py` | PAP      | PAP    |
| `ci.py`         | CI       | CI     |

Add your checker to the existing module for its category, or create a new
module if introducing a new category.

## Step 2: Implement the checker

```python
from oss_paper_ci.checks.base import BaseChecker, CheckContext
from oss_paper_ci.checks import register
from oss_paper_ci.models import CheckResult


@register
class MyNewChecker(BaseChecker):
    check_id = "EXP007"
    title = "Experiment logging detected"
    severity = "info"
    category = "EXP"
    description = "Checks whether experiment logging tools are configured."

    def check(self, ctx: CheckContext) -> list[CheckResult]:
        # Use ctx to inspect the repository
        if ctx.has_file("mlruns") or ctx.has_file("runs"):
            return [self._pass("Experiment logging directory found.")]

        # Search for logging imports in Python files
        for f in ctx.files:
            if f.suffix == ".py":
                content = ctx.read_file(str(f.relative_to(ctx.root)))
                if content and ("mlflow" in content or "wandb" in content):
                    return [self._pass("Experiment logging import found.", evidence=[str(f.name)])]

        return [self._warn(
            "No experiment logging detected.",
            recommendation="Add MLflow, Weights & Biases, or similar logging to track experiments.",
        )]
```

## Step 3: Set class attributes

| Attribute         | Type   | Required | Description                                      |
|-------------------|--------|----------|--------------------------------------------------|
| `check_id`        | str    | Yes      | Unique ID, e.g. `EXP007`. Prefix matches category. |
| `title`           | str    | Yes      | Short human-readable title.                      |
| `severity`        | str    | Yes      | One of `error`, `warning`, `info`.               |
| `category`        | str    | Yes      | Category prefix (e.g. `EXP`).                    |
| `description`     | str    | No       | Longer description shown by `explain` command.   |
| `default_enabled` | bool   | No       | Whether the check runs by default (default: True). |

## Step 4: Use CheckContext

`CheckContext` provides access to the repository during scanning:

| Method / Property       | Returns       | Description                                    |
|-------------------------|---------------|------------------------------------------------|
| `ctx.repo_path`         | str           | Absolute path to the repository root.          |
| `ctx.root`              | Path          | `Path` object for the repo root.               |
| `ctx.config`            | Config        | The loaded configuration object.               |
| `ctx.files`             | list[Path]    | All files in the repo (excluding ignored paths).|
| `ctx.has_file(*parts)`  | bool          | Check if a file exists relative to root.       |
| `ctx.read_file(*parts)` | str or None   | Read a file's contents. Returns None on error. |
| `ctx.file_names()`      | set[str]      | Set of all file names (not full paths).        |
| `ctx.file_suffixes()`   | set[str]      | Set of all file extensions in the repo.        |

## Step 5: Return CheckResult objects

Use the helper methods on `BaseChecker`:

| Helper                                        | Status | Severity set to  |
|-----------------------------------------------|--------|------------------|
| `self._pass(message, evidence=None)`          | pass   | (unchanged)      |
| `self._warn(message, evidence, recommendation)`| warn  | warning          |
| `self._fail(message, evidence, recommendation)`| fail  | error            |
| `self._unknown(message, evidence)`            | unknown| (unchanged)      |

Each method returns a `CheckResult` with the check's `id` and `title` filled in.

## Step 6: Add tests

Add test cases in `tests/` that cover:

1. **Pass case:** A repository fixture that should pass the check.
2. **Fail case:** A repository fixture that should fail the check.
3. **Edge case:** Empty repo, missing files, malformed content.

Use the existing test fixtures in `tests/fixtures/` as examples.

## Naming conventions

- Check IDs use the category prefix followed by a zero-padded number:
  `META001`, `ENV003`, `EXP007`.
- Titles are sentence fragments without trailing punctuation:
  "Experiment logging detected", not "Experiment logging detected."
- Recommendations are imperative sentences:
  "Add MLflow or Weights & Biases to track experiments."

## Registering a new module

If you create a new category (e.g., `security.py`), add the import to
`src/oss_paper_ci/checks/registry.py` in the `_ensure_loaded()` function:

```python
from oss_paper_ci.checks import (  # noqa: F401
    metadata,
    environment,
    experiments,
    data,
    results,
    paper_code,
    ci,
    security,  # new module
)
```

Also add a category cap in `src/oss_paper_ci/scoring.py`:

```python
_CATEGORY_CAP: dict[str, int] = {
    ...
    "SEC": 10,  # new category
}
```
