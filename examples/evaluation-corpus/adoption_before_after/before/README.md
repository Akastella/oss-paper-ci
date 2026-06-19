# Before: Minimal Python Project

This is a synthetic test fixture showing a minimal Python project **without** reproducibility files.

**This is NOT a real project.** It is a test fixture for oss-paper-ci evaluation.

## What's Missing

- No requirements.txt or pyproject.toml
- No data documentation
- No reproducibility.yml
- No results directory
- No LICENSE

## Expected Behavior

oss-paper-ci should detect:
- Missing environment specification
- Missing data documentation
- Low reproducibility score
