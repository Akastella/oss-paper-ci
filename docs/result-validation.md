# Result Validation

The `results validate` command checks the existence and format of
declared result artifacts.

## What It Checks

1. **Results directory**: Does `results/` exist?
2. **Metrics file**: Does `metrics.json` exist and is it valid JSON?
3. **Metrics schema**: Are metric values numeric or interpretable?
4. **Figures directory**: Does `figures/` exist?
5. **Tables directory**: Does `tables/` exist?
6. **Expected artifacts**: Do declared outputs exist?
7. **Large result files**: Are there files > 50MB?

## Usage

```bash
# Markdown output
oss-paper-ci results validate /path/to/repo

# JSON output
oss-paper-ci results validate /path/to/repo --format json

# Write to file
oss-paper-ci results validate /path/to/repo --output validation.md
```

## Important Notes

- This tool checks artifact existence, NOT scientific correctness
- A valid metrics.json does not mean the metrics are correct
- Expected artifacts are read from `reproducibility.yml`
- Missing artifacts may indicate the reproduction hasn't been run

## See Also

- [Data Diagnostics](data-diagnostics.md)
- [Evidence Scores](evidence-scores.md)
- [Limitations](limitations.md)
