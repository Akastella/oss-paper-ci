# Design Principles

These principles guide every decision in oss-paper-ci.

## Deterministic

Same input produces the same output. Every check is a rule-based inspection
of files and text patterns. There is no randomness, no LLM, no heuristics
that drift over time. If you run the tool twice on the same repository, you
get the same score.

## Offline

No network calls. No API keys. No telemetry. The tool works entirely on the
local filesystem. It does not fetch external resources, check PyPI for package
existence, or phone home. You can run it on an air-gapped machine.

## Explainable

Every check result includes:

- **Evidence:** The specific files or patterns that triggered the result.
- **Recommendation:** A concrete action the user can take to fix the issue.

There are no black-box scores. If a check fails, you can see exactly why and
what to do about it. Use `oss-paper-ci explain <CHECK_ID>` to get detailed
documentation for any check.

## Non-judgmental

The tool evaluates repository engineering, not research quality. A high score
means the repo is well-structured for reproducibility -- it says nothing about
whether the science is correct. A low score means the repo is missing common
engineering practices -- it does not mean the research is bad.

The language in reports is factual and actionable. It does not use words like
"bad", "poor", or "failing". It says "not found" and tells you how to add it.

## Extensible

New checks are added by:

1. Subclassing `BaseChecker` in `src/oss_paper_ci/checks/`.
2. Setting `check_id`, `title`, and `severity`.
3. Implementing the `check()` method.
4. Decorating with `@register`.

The registry discovers all checkers automatically. No configuration file
needs to be updated. See `src/oss_paper_ci/checks/base.py` for the interface.

## CI-native

The tool is designed to run in CI pipelines:

- Exit codes map to pipeline states: `0` = all pass, `1` = warnings only, `2` = failures.
- Output formats include Markdown (for artifacts) and JSON (for programmatic use).
- The `--format` flag controls output. The `-o` flag writes to a file.
- No interactive prompts. No TUI. No colors in file output.

A GitHub Actions workflow example is included in the README.
