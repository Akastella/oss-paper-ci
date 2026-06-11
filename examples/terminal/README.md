# Terminal Examples

This directory contains example outputs from the terminal workbench,
wizard, and theme preview commands.

## Files

| File | Command | Description |
|------|---------|-------------|
| `wizard_output.txt` | `oss-paper-ci wizard --plain .` | Guided wizard output |
| `workbench_plain_output.txt` | `oss-paper-ci workbench examples/demo-reproduce-repo --plain` | Workbench pipeline output |
| `theme_preview.md` | `oss-paper-ci theme preview --plain` | Theme preview with sample data |
| `workbench_pretty_preview.md` | (documented) | Rich terminal preview description |

## Generating

```bash
# Wizard
oss-paper-ci wizard --plain . > examples/terminal/wizard_output.txt

# Workbench
oss-paper-ci workbench examples/demo-reproduce-repo --plain --output-dir /tmp/wb-out > examples/terminal/workbench_plain_output.txt
rm -rf /tmp/wb-out

# Theme preview
oss-paper-ci theme preview --plain > examples/terminal/theme_preview.md
```

## Rich Terminal Preview

When running in a TTY without `--plain`, the workbench displays:

```
========================================================================
  OSS-Paper-CI Workbench
  Repository: /path/to/repo
  Mode: safe dry-run
========================================================================

 [1/5] Detect ecosystems                        OK
    Python
 [2/5] Scan repository                          !
    Score: 72/100, 3 findings
 [3/5] Data diagnostics                         OK
    All checks passed
 [4/5] Validate results                         X
    2 issue(s)
 [5/5] Generate dossier                         OK
    Reproducibility dossier generated

  Score: 72/100
    metadata: 85/100
    environment: 60/100
    experiments: 70/100
    data: 55/100
    results: 80/100

------------------------------------------------------------------------
  Summary
------------------------------------------------------------------------
  ! Overall readiness: needs work
  X Validate results: 2 issue(s)
------------------------------------------------------------------------

------------------------------------------------------------------------
  Suggested Next Actions
------------------------------------------------------------------------
    1. Check that claimed results trace to evidence files.
------------------------------------------------------------------------
```

Colors are applied automatically in supported terminals.
Use `--plain` or `--theme minimal` for CI-friendly output.
