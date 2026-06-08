# Troubleshooting

## Installation Issues

### Editable install fails
```bash
pip install -e ".[dev]"
# If this fails, try:
pip install -e . --no-build-isolation
```

### Windows path issues
- Use forward slashes in config files
- The tool normalizes paths internally
- Report path issues with your OS and Python version

## GitHub Actions Issues

### Permission denied for PR comments
Add to your workflow:
```yaml
permissions:
  pull-requests: write
```

### SARIF upload fails
Add to your workflow:
```yaml
permissions:
  security-events: write
```

## Smoke Runner Issues

### Command blocked by security policy
The smoke runner blocks dangerous commands. Check if your command contains:
- `rm -rf`, `sudo`, `curl | sh`, `wget | sh`
- Absolute path writes
- PowerShell `Invoke-Expression`

### Timeout
Default timeout is 60 seconds. Increase with `--timeout 120`.

## Baseline Issues

### Compare fails
Ensure the baseline file exists and was created with the same tool version.

## YAML Parsing Issues

### Config file not recognized
Ensure your `oss-paper-ci.yml` uses valid YAML syntax. Check indentation.

## Cross-Language Issues

### R/Julia/MATLAB not detected
Ensure your project has the standard files for that language:
- R: `DESCRIPTION`, `renv.lock`, `.R` scripts
- Julia: `Project.toml`, `.jl` scripts
- MATLAB: `.m` files, `startup.m`
