# DSL Safety Checks and Declarations

The DSL safety system checks reproduction commands for dangerous patterns,
undeclared network/install operations, secret exposure, and path traversal.
Safety checks are read-only; they report findings but never block file access
or modify anything.

## Safety declarations

Every `reproducibility.yml` can declare safety constraints:

```yaml
safety:
  network: false       # Steps may not access the network
  allow_install: false # Steps may not install packages at runtime
  allow_gpu: false     # Steps may not request GPU resources
```

All flags default to `false` (most restrictive).  The safety system checks
whether step commands are consistent with these declarations.

## What gets checked

### 1. Blocked commands (always blocked)

These patterns are blocked regardless of safety settings:

| Pattern                     | Description                   |
|-----------------------------|-------------------------------|
| `rm -rf /`                  | Root filesystem deletion      |
| `curl \| sh`                | Pipe to shell                 |
| `wget \| bash`              | Pipe to shell                 |
| `sudo`                      | Privilege escalation          |
| `chmod 777 /`               | System permission change      |
| `mkfs`                      | Filesystem format             |
| `dd if=... of=`             | Raw disk write                |
| Fork bomb (`:(){ ... }`)    | Process exhaustion            |
| `> /etc/`                   | Write to system directories   |
| `git push --force`          | Destructive git operation     |
| `gh repo delete`            | Repository deletion           |
| `npm publish`               | Package publication           |
| `shutdown` / `reboot`       | System shutdown               |
| `base64 -d`                 | Encoding evasion              |

Commands matching these patterns cause the safety level to be `"blocked"` and
the step to be marked as blocked in the execution plan.

### 2. Undeclared network usage

If `safety.network` is `false`, commands containing network operations produce
warnings:

| Pattern           | Description           |
|-------------------|-----------------------|
| `curl`            | HTTP request          |
| `wget`            | HTTP download         |
| `git clone`       | Repository clone      |
| `git pull`        | Repository update     |
| `pip install`     | Package download      |
| `conda install`   | Package download      |
| `npm install`     | Package download      |
| `apt-get install` | System package        |
| `brew install`    | System package        |

### 3. Undeclared install operations

If `safety.allow_install` is `false`, commands containing install operations
produce warnings:

| Pattern             | Description            |
|---------------------|------------------------|
| `pip install`       | Python package install |
| `conda install`     | Conda package install  |
| `npm install`       | Node package install   |
| `cargo install`     | Rust package install   |
| `apt-get install`   | System package install |
| `gem install`       | Ruby gem install       |
| `composer install`  | PHP dependency install |

### 4. Secret exposure

Commands referencing environment variables that may contain secrets produce
warnings:

| Pattern                    | Description              |
|----------------------------|--------------------------|
| `$SECRET*`                 | Generic secret variable  |
| `$TOKEN*`                  | Token variable           |
| `$PASSWORD*`               | Password variable        |
| `$API_KEY*`                | API key variable         |
| `$AWS_SECRET*`             | AWS secret key           |
| `echo ... $SECRET`         | Echo secret to stdout    |
| `cat .env`                 | Reading .env file        |

### 5. Path safety

Paths in `produces`, `datasets`, and `artifacts` are checked for:

- **Path traversal**: `../` sequences
- **Absolute system paths**: `/etc/`, `/usr/`, `/bin/`, `/root/`, `/home/`

## Safety levels

The safety report assigns one of three levels:

| Level      | Condition                                          |
|------------|----------------------------------------------------|
| `"safe"`   | No findings                                        |
| `"caution"`| Warnings present (undeclared network/install, etc.) |
| `"blocked"`| At least one command matches a blocked pattern     |

## CLI usage

```bash
# Validate (includes safety checks)
oss-paper-ci dsl validate reproducibility.yml

# Plan (includes safety checks)
oss-paper-ci dsl plan reproducibility.yml --format markdown

# Explain (includes safety findings)
oss-paper-ci dsl explain reproducibility.yml --format json
```

Safety findings appear in the validation and plan reports.  There is no
separate `dsl safety` command; safety is always checked as part of validation
and planning.

## Example: undeclared network

```yaml
safety:
  network: false

steps:
  download:
    command: wget https://example.com/model.bin -O results/model.bin
    needs: []
```

This produces a warning:

```
Undeclared network usage: wget
```

To resolve, either:
- Set `safety.network: true` if network access is intentional.
- Remove the network command and declare the file as a dataset.

## Example: blocked command

```yaml
steps:
  setup:
    command: sudo pip install torch
    needs: []
```

This produces a blocked finding:

```
Blocked: sudo command
```

The step is marked as blocked in the execution plan and cannot be executed.

## Example: undeclared install

```yaml
safety:
  allow_install: false

steps:
  setup:
    command: pip install transformers
    needs: []
```

This produces a warning:

```
Undeclared install operation: pip install
```

To resolve, either:
- Set `safety.allow_install: true` if runtime installs are intentional.
- Move the install to `environments.*.install` so it runs during setup.

## Behavior notes

- Safety checks are read-only.  They report findings but never execute commands.
- Blocked commands cause the plan to mark those steps as blocked.
- The tool never auto-executes, auto-installs, or auto-fixes code.
- Safety findings are included in validation reports, plan reports, and
  explanation reports.
- The `requires_explicit_execute` flag is set to `true` when blocked commands,
  network usage, or install operations are detected.  This flag signals that
  explicit user approval is needed before execution.

## Related documentation

- [Reproducibility DSL Overview](reproducibility-dsl.md)
- [Reproducibility Schema v1](reproducibility-schema-v1.md)
- [DAG Planner](dag-planner.md)
- [DSL Examples](dsl-examples.md)
