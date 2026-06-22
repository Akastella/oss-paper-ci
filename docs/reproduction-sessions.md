# Reproduction Sessions

Reproduction sessions track the lifecycle of a reproduction attempt: planning, execution, status, logs, artifacts, metrics, and failure reasons. Sessions support resuming interrupted runs, re-running failed steps, and comparing results across configurations.

## Usage

```bash
# Start a session (dry-run by default)
oss-paper-ci session start .

# Start with a name
oss-paper-ci session start . --name my-session

# Start with explicit config
oss-paper-ci session start . --config reproducibility.yml

# Check session status
oss-paper-ci session status .oss-paper-ci-sessions/my-session

# Generate session report
oss-paper-ci session report .oss-paper-ci-sessions/my-session --format markdown
oss-paper-ci session report .oss-paper-ci-sessions/my-session --format json
oss-paper-ci session report .oss-paper-ci-sessions/my-session --format html

# Create evidence bundle
oss-paper-ci session bundle .oss-paper-ci-sessions/my-session --output session-evidence.zip

# Inspect bundle
oss-paper-ci session inspect session-evidence.zip

# Verify bundle integrity
oss-paper-ci session verify-bundle session-evidence.zip
```

## Session Lifecycle

1. **Plan**: Session is created from `reproducibility.yml` with all commands in `pending` state
2. **Execute**: Commands are run in dependency order (only with `--execute`)
3. **Track**: Status, duration, exit codes, stdout/stderr are recorded per command
4. **Resume**: Interrupted sessions can be resumed; passed commands are skipped
5. **Re-run**: Failed commands can be re-run without re-running passed ones
6. **Report**: Generate Markdown, JSON, or HTML reports
7. **Bundle**: Create a ZIP evidence bundle for archival

## Session Directory Layout

```
.oss-paper-ci-sessions/<name>/
  session.json          # Session manifest
  plan.json             # Command plan
  runs/
    <command_id>/
      command.json      # Command metadata
      stdout.txt        # Standard output
      stderr.txt        # Standard error
  reports/
    session.md          # Markdown report
    session.json        # JSON report
    session.html        # HTML report
  SHA256SUMS            # File checksums
```

## Resume

Resume a paused or interrupted session:

```bash
# Show what will be resumed (dry-run)
oss-paper-ci session resume .oss-paper-ci-sessions/my-session

# Actually resume
oss-paper-ci session resume .oss-paper-ci-sessions/my-session --execute
```

Resume skips commands that already passed and re-runs pending, failed, or timed-out commands.

## Re-run Failed

Re-run only the failed commands:

```bash
# Show what will be re-run (dry-run)
oss-paper-ci session rerun-failed .oss-paper-ci-sessions/my-session

# Actually re-run
oss-paper-ci session rerun-failed .oss-paper-ci-sessions/my-session --execute
```

Re-run only selects commands with `failed` or `timeout` status. Blocked commands are not re-run.

## Session Status

| Status | Description |
|--------|-------------|
| `planned` | Session created, no commands executed |
| `running` | Commands are being executed |
| `passed` | All commands passed |
| `failed` | One or more commands failed |
| `partial` | Some commands executed, some still pending |

## Safety

- Sessions are **dry-run by default**; `--execute` is required for execution
- Dangerous commands are **blocked** and not executed
- Blocked commands are not re-run by resume or rerun-failed
- Session directories are local and not committed to git
- No network access is performed
- No dependencies are installed

## See Also

- [Reproduction Matrix](reproduction-matrix.md) — Run across multiple configurations
- [Session Bundles](session-bundles.md) — Create and verify evidence bundles
- [Session Safety](session-safety.md) — Detailed safety model
- [Reproduction Orchestrator](reproduction-orchestrator.md) — Underlying execution engine
