# Wizard

The wizard provides guided setup for new users.

## Usage

```bash
oss-paper-ci wizard
oss-paper-ci wizard --plain
```

## What It Does

1. Detects your repository characteristics (config, data directory, CI, git)
2. Recommends safe next-step commands based on what it finds
3. Shows the commands you can run — does **not** execute them automatically

## Example Output

```
========================================================================
  OSS-Paper-CI Wizard
  Guided setup for reproducibility checking
========================================================================

  Repository
  Path: /home/user/my-paper
  Git: detected
  Config: not found

  1. Check your repository: Scan for reproducibility readiness.
     $ oss-paper-ci scan .

  2. Create a configuration file: Generate oss-paper-ci.yml.
     $ oss-paper-ci init --dry-run

  3. Run the workbench: Full pipeline with summary.
     $ oss-paper-ci workbench . --plain
```

## Non-Interactive Mode

In CI or non-TTY environments, the wizard prints recommendations without
blocking for input. Use `--plain` for clean machine-readable output.

## Related

- [Workbench](terminal-workbench.md) — run the full pipeline
- [Getting Started](getting-started.md) — installation and first steps
