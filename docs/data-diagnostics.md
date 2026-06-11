# Data Diagnostics

The `data diagnose` command checks data availability, documentation,
and metadata in a repository.

## What It Checks

1. **Data directory**: Does `data/` exist?
2. **Data documentation**: Does `data/README.md` exist?
3. **Availability statement**: Does README mention data sources?
4. **External data URLs**: Are external data links declared?
5. **Sample data**: Is sample/example data present?
6. **Large files**: Are there files > 10MB that should be excluded?
7. **Gitignore patterns**: Are data files excluded from version control?
8. **Data license**: Is data usage documented?

## Usage

```bash
# Markdown output
oss-paper-ci data diagnose /path/to/repo

# JSON output
oss-paper-ci data diagnose /path/to/repo --format json

# Write to file
oss-paper-ci data diagnose /path/to/repo --output diagnostics.md
```

## Important Notes

- This tool does NOT download or verify data online
- It only checks static declarations and file presence
- "External data URLs found" means URLs were detected, not that they are valid
- Missing data documentation is a warning, not an error

## See Also

- [Result Validation](result-validation.md)
- [Evidence Scores](evidence-scores.md)
- [Limitations](limitations.md)
