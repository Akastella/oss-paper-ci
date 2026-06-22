# Adapter Safety

## Safety Invariants

1. **Default to dry-run**: All adapters generate plans without executing
2. **No auto-install**: Runtimes are never automatically installed
3. **No auto-network**: Network access requires explicit flags
4. **No auto-modify**: User projects are never modified
5. **Block dangerous commands**: Shell adapter blocks `rm -rf /`, `curl | bash`, etc.
6. **Report missing runtimes**: Missing runtime = unavailable, not error

## Shell Script Safety

The shell adapter checks for dangerous patterns:
- `rm -rf /`
- `curl | bash` / `wget | bash`
- `mkfs.`
- Fork bombs

Scripts with dangerous patterns are flagged in the plan output.
