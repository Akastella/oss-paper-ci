# Shell Adapter

The Shell adapter detects shell script projects and provides dangerous command blocking.

## Detection

Files detected:
- `run.sh`, `reproduce.sh`, `scripts/*.sh`, `*.sh`, `setup.sh`

## Planning

Run steps are generated for detected shell scripts. Scripts are checked for dangerous patterns.

## Runtime

Requires: `bash`

Support level: **execute-if-runtime-present**

## Dangerous Command Blocking

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

Scripts containing these patterns are flagged as dangerous in the plan.

## Limitations

- Shell scripts may have system-specific dependencies
- Scripts may require specific tools to be installed
- Not all dangerous patterns may be detected

## Safety

- All shell scripts are checked for dangerous patterns before execution
- Dangerous scripts are flagged but not automatically blocked at plan time
- Actual execution requires `--execute` flag
