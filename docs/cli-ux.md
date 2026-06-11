# CLI UX Guide

OSS-Paper-CI provides a terminal-friendly interface with automatic
degradation for non-interactive environments.

## Output Modes

| Mode | Color | Animation | Rich panels | Use case |
|------|-------|-----------|-------------|----------|
| Default (TTY) | Yes | Yes | Yes | Interactive terminal |
| `--plain` | No | No | No | Scripts, pipes |
| `--no-color` | No | Yes | No | Color-unsupported terminals |
| `--no-animate` | Yes | No | Yes | Slow connections |
| CI (auto-detected) | No | No | No | GitHub Actions, etc. |

## Global Flags

```bash
oss-paper-ci --plain wizard .
oss-paper-ci --no-color workbench .
oss-paper-ci --theme contrast scan .
oss-paper-ci --debug workbench .
```

| Flag | Effect |
|------|--------|
| `--plain` | Force plain text (no color, no animation, no rich) |
| `--no-color` | Disable color output |
| `--no-animate` | Disable spinners and progress animation |
| `--theme NAME` | Select terminal theme |
| `--debug` | Show tracebacks on error |

## Environment Variables

| Variable | Effect |
|----------|--------|
| `NO_COLOR=1` | Disable color (standard convention) |
| `OSS_PAPER_CI_NO_COLOR=1` | Disable color |
| `OSS_PAPER_CI_NO_ANIMATE=1` | Disable animation |
| `OSS_PAPER_CI_PLAIN=1` | Force plain mode |

## Components

- **Title banner** — project name and context
- **Step progress** — numbered steps with status indicators
- **Score display** — overall score with component breakdown
- **Summary panel** — key findings at a glance
- **Next actions** — suggested commands to run
- **Error cards** — structured error explanations

## Backward Compatibility

All existing commands, flags, and output formats are preserved.
JSON, Markdown, HTML, and SARIF outputs never contain ANSI codes.
The new UI is additive — it only activates for the new commands
(wizard, workbench, theme preview).
