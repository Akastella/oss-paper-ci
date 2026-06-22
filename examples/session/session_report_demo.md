# Reproduction Session Report 📋

**Tool:** oss-paper-ci 3.3.0rc1
**Session ID:** `111e695421c2`
**Name:** demo
**Status:** planned

## Summary

| Metric | Count |
|--------|-------|
| Total | 3 |
| Passed | 0 |
| Failed | 0 |
| Blocked | 0 |
| Timeout | 0 |
| Pending | 3 |

## Commands

| ID | Status | Duration | Exit | Command |
|-----|--------|----------|------|---------|
| train | ⏳ pending | - | - | `python scripts/train.py` |
| evaluate | ⏳ pending | - | - | `python scripts/evaluate.py` |
| make_figures | ⏳ pending | - | - | `python scripts/make_figures.py` |

## Limitations
- Session commands are declared in reproducibility.yml.
- Default mode is dry-run; use --execute to run commands.
- Blocked dangerous commands are not executed.
