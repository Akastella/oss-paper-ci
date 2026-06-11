# Terminal Workbench

The workbench runs a multi-step reproducibility pipeline in a single command.

## Usage

```bash
oss-paper-ci workbench .
oss-paper-ci workbench . --output-dir oss-paper-ci-out
oss-paper-ci workbench . --plain
oss-paper-ci workbench . --theme minimal
```

## Pipeline Steps

1. **Detect ecosystems** — identify language runtimes (Python, R, Julia, etc.)
2. **Scan repository** — run all reproducibility checks and compute a score
3. **Data diagnostics** — verify data documentation and availability
4. **Validate results** — check that claimed results trace to evidence
5. **Generate dossier** — produce a human-readable reproducibility summary

## Output Files

When `--output-dir` is specified:

| File | Description |
|------|-------------|
| `workbench.json` | Machine-readable pipeline result |
| `summary.md` | Human-readable markdown summary |
| `scan.json` | Full scan report |
| `data-diagnostics.json` | Data diagnostics results |
| `result-validation.json` | Result validation results |
| `ecosystems.json` | Detected ecosystems |
| `dossier.md` | Reproducibility dossier |

## Options

| Flag | Description |
|------|-------------|
| `--output-dir DIR` | Write results to directory |
| `--force` | Overwrite existing output directory |
| `--with-reproduce-dry-run` | Include reproduce dry-run step |
| `--plain` | Plain text output (no color/animation) |
| `--no-color` | Disable color |
| `--no-animate` | Disable animation |
| `--theme NAME` | Select theme (classic, minimal, contrast) |

## Safety

The workbench is **safe by default**:

- No experiments are executed
- No dependencies are installed
- No remote scripts are run
- All analysis is read-only

## CI Usage

```yaml
- name: Run workbench
  run: oss-paper-ci workbench . --plain --output-dir results
  env:
    NO_COLOR: "1"
```
