# Reproduction Report

The reproduce command generates a structured report documenting the
reproduction attempt.

## Report Fields

| Field | Description |
|-------|-------------|
| `input_url` | User-provided URL or path |
| `repo_url` | Resolved repository URL |
| `paper_url` | Paper URL (if provided) |
| `resolved_source` | Source type: github, local, paper |
| `commit_sha` | Git commit SHA of the cloned repo |
| `environment_files` | Detected environment files |
| `install_plan` | Planned installation steps |
| `install_result` | Actual installation results |
| `reproduction_commands` | Commands to be run |
| `command_results` | Actual command execution results |
| `generated_artifacts` | Files generated during reproduction |
| `scan_score` | oss-paper-ci scan score |
| `scan_status` | Scan pass/warn/fail status |
| `scan_findings_summary` | Summary of scan findings |
| `limitations` | Known limitations of the attempt |
| `rerun_commands` | Exact commands to rerun locally |

## Output Formats

### Markdown

Human-readable format suitable for GitHub issues or PR comments.
Includes collapsible sections for stdout/stderr.

```bash
oss-paper-ci reproduce URL --format markdown --output report.md
```

### JSON

Machine-readable format for programmatic consumption.

```bash
oss-paper-ci reproduce URL --format json --output report.json
```

### HTML

Single-file HTML report with no external CDN dependencies.
All content is HTML-escaped. Suitable for sharing or archiving.

```bash
oss-paper-ci reproduce URL --format html --output report.html
```

## Report Status

The report uses these status indicators:

- **dry-run**: no commands were executed
- **ok**: command completed successfully (exit code 0)
- **FAILED**: command failed (non-zero exit code)
- **BLOCKED**: command was blocked by safety check
- **Timed out**: command exceeded timeout

## Disclaimer

Every report includes a disclaimer:

> This is an *attempted reproduction report*. It documents what commands
> were run (or would be run), not whether the paper's claims are correct.
> Successful command execution does not mean the paper's results are valid
> or reproducible.
