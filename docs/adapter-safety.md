# Adapter Safety

## Safety Invariants

1. **Default to dry-run**: All adapters generate plans without executing
2. **No auto-install**: Runtimes are never automatically installed
3. **No auto-network**: Network access requires explicit flags
4. **No auto-modify**: User projects are never modified
5. **Block dangerous commands**: Shell adapter blocks `rm -rf /`, `curl | bash`, etc.
6. **Report missing runtimes**: Missing runtime = unavailable, not error

## Per-Adapter Safety

### Python
- Commands checked for `rm -rf /` patterns
- Virtual environment isolation for installs

### R
- `install.packages()` calls flagged as warnings

### Julia
- `Pkg.add()` calls flagged as warnings

### Shell
- Comprehensive dangerous pattern blocking (see [shell-adapter.md](shell-adapter.md))
- Scripts with dangerous patterns are flagged in plans

### MATLAB/Snakemake/Nextflow
- **Dry-run only** — execution is not supported
- These adapters only detect and plan, never execute

## Shell Script Safety

The shell adapter blocks the following patterns:

| Pattern | Description |
|---------|-------------|
| `rm -rf /` | Recursive delete from root |
| `rm -rf ~` | Recursive delete of home |
| `curl \| bash` | Pipe curl to shell |
| `wget \| bash` | Pipe wget to shell |
| `curl \| sh` | Pipe curl to sh |
| `wget \| sh` | Pipe wget to sh |
| `eval $(curl` | Eval curl output |
| `eval $(wget` | Eval wget output |
| `mkfs.` | Format filesystem |
| `dd if=` | Direct disk write |
| `> /dev/sd` | Write to disk device |
| `chmod -R 777 /` | World-writable permissions |

Scripts with dangerous patterns are flagged in the plan output.

## Runtime Missing

When a required runtime is not available:
- Detection still works (files are scanned)
- Planning still works (steps are generated)
- Execution is skipped
- Output shows `available: false` with install suggestion

## What Is Not Checked

- Network requests within executed code
- File system modifications beyond the working directory
- Side effects of compiled code
- Behavior of third-party dependencies
