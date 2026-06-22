# Intake Safety

The intake system is designed with safety as a primary concern. It is a **read-only** operation that never modifies the repository or executes code.

## Core Safety Principles

### 1. Read-Only

Intake only reads files from the repository. It never:
- Creates files
- Modifies files
- Deletes files
- Changes permissions
- Commits to git

### 2. No Execution

Intake never executes any commands found in the repository. It only:
- Reads command text from documentation
- Classifies commands by kind
- Flags dangerous commands
- Reports findings

### 3. No Network Access

Intake never makes network requests by default:
- No HTTP requests
- No git clone (unless explicit `--clone`)
- No package downloads
- No API calls

### 4. No Dependency Installation

Intake never installs dependencies:
- No `pip install`
- No `npm install`
- No `conda install`
- No package manager operations

## Dangerous Command Detection

Commands matching these patterns are flagged as dangerous:

### Disk/Filesystem Destruction
- `rm -rf /`, `rm -rf /*`
- `rmdir /s /q`, `format`, `mkfs`
- `dd if=`, fork bombs

### Privilege Escalation
- `sudo`, `su -`
- `chmod 777`, `chown root`

### Network/Remote Execution
- `curl | sh`, `wget | bash`
- `powershell Invoke-Expression`

### Destructive Git Operations
- `git push`, `git push --force`
- `git clean -fd`, `git reset --hard`

### Repository Destruction
- `gh repo delete`, `gh repo archive`

### Package Manager Abuse
- `npm publish`, `twine upload`

## GitHub URL Safety

When a GitHub URL is provided:
- Without `--clone`: Only the URL is parsed; no network request
- With `--clone`: Shallow clone (depth=1), no submodules, with timeout
- Clone failure produces a warning, not a crash

## Paper URL Safety

When a paper URL is provided:
- No network request is made
- No paper content is fetched
- A warning is generated about needing a repository path

## Autoplan Safety

The autoplan system extends intake safety:
- Candidate plans are marked `generated_mode: candidate`
- `--write` is required to write the config
- `--force` is required to overwrite existing files
- Dangerous commands are excluded from candidate plans
- No commands are executed during autoplan
