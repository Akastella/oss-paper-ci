# Session Safety

Reproduction sessions are designed with safety as a primary concern. They extend the existing reproduction orchestrator safety model.

## Core Safety Principles

### 1. Dry-Run by Default

Sessions start in dry-run mode:
- Commands are planned but not executed
- Status shows `pending` for all commands
- Only `--execute` triggers actual execution

### 2. Dangerous Command Blocking

Commands matching dangerous patterns are blocked:
- `sudo`, `rm -rf /`, `curl | sh`, `wget | bash`
- `git push`, `npm publish`, `twine upload`
- `shutdown`, `reboot`, `kill -9 1`

Blocked commands:
- Are marked with `status: blocked`
- Include a `block_reason`
- Are **never** executed
- Are **not** re-run by resume or rerun-failed

### 3. No Auto-Installation

Sessions never install dependencies:
- No `pip install`
- No `npm install`
- No `conda install`
- No package manager operations

### 4. No Network Access

Sessions never make network requests:
- No HTTP requests
- No git clone
- No package downloads
- No API calls

### 5. No Repository Modification

Sessions do not modify the original repository:
- Commands run in the repository directory
- But session data is stored in a separate directory
- No git commits
- No file modifications to tracked files

## Matrix Safety

Matrix execution inherits all session safety rules:
- Each variant is an independent session
- Each variant has the same safety checks
- Missing runtimes are marked `unavailable`, not installed
- Dangerous commands are blocked in all variants

## Resume Safety

Resume and rerun-failed maintain safety:
- Only pending/failed/timeout commands are re-run
- Passed commands are skipped
- Blocked commands are never re-run
- Each attempt is recorded in history

## Bundle Safety

Session bundles are safe:
- Only contain session metadata, logs, and reports
- Do not contain repository source code
- Do not contain secrets or credentials
- SHA256SUMS for integrity verification
