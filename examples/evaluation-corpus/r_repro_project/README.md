# Synthetic Test Fixture: R Reproducible Project

**This is a synthetic test repository for oss-paper-ci evaluation. It is NOT a real project.**

## Overview

This fixture simulates an R project with good reproducibility practices, including renv for dependency management.

## Project Structure

- `scripts/run_analysis.R` - Main analysis script
- `data/README.md` - Data documentation
- `results/results.json` - Analysis results
- `DESCRIPTION` - R package description
- `renv.lock` - Dependency lock file

## Reproducibility

This project uses `renv` for dependency management. To restore the environment:

```r
renv::restore()
```

## Data Availability

The dataset used in this study is available at [placeholder URL]. See `data/README.md` for details.

## License

MIT License - see [LICENSE](LICENSE)
