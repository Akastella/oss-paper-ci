# Workbench Pretty Preview

This document describes the rich terminal output when running
`oss-paper-ci workbench` in an interactive terminal.

## Title Banner

```
========================================================================
  OSS-Paper-CI Workbench
  Repository: /home/user/my-paper
  Mode: safe dry-run
========================================================================
```

## Step Progress

Each step shows a numbered indicator with status:

```
 [1/5] Detect ecosystems                        OK
 [2/5] Scan repository                          !
 [3/5] Data diagnostics                         X
 [4/5] Validate results                         OK
 [5/5] Generate dossier                         OK
```

Status symbols:
- `OK` — step passed
- `!` — step has warnings
- `X` — step failed
- `-` — step skipped

## Score Display

```
  Score: 72/100
    metadata: 85/100
    environment: 60/100
    experiments: 70/100
    data: 55/100
    results: 80/100
```

## Summary Panel

```
------------------------------------------------------------------------
  Summary
------------------------------------------------------------------------
  ! Overall readiness: needs work
  OK Detect ecosystems: Python
  ! Scan repository: Score: 72/100, 3 findings
  OK Data diagnostics: All checks passed
  X Validate results: 2 issue(s)
  OK Generate dossier: Reproducibility dossier generated
------------------------------------------------------------------------
```

## Next Actions

```
------------------------------------------------------------------------
  Suggested Next Actions
------------------------------------------------------------------------
    1. Check that claimed results trace to evidence files.
    2. Run 'oss-paper-ci scan . --verbose' for details.
------------------------------------------------------------------------
```

## Theme Variations

- **classic** — green/red/yellow with Unicode symbols (default)
- **minimal** — plain text icons, reduced color
- **contrast** — bold white text for accessibility

Use `oss-paper-ci theme preview` to see your current theme in action.
