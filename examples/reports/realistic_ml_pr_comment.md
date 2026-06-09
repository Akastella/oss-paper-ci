## Reproducibility Report

**Score:** 93/100
**Status:** pass
**Checks:** 0 pass, 18 warn, 4 fail

### Findings (showing 10 of 15)

- **! META005**: No contributing guidelines found.
  - Recommendation: Consider adding a CONTRIBUTING.md file or an issue template to encourage community contributions.
- **! ENV006**: Both pyproject.toml and requirements.txt exist but no clear guidance found in README
  - Recommendation: Document in the README which file (pyproject.toml or requirements.txt) users should use and under what circumstances.
- **! EXP007**: Found 1 notebook(s) with script alternatives available.
- **! DATA003**: No distinction between data categories found.
  - Recommendation: Consider organizing your data into subdirectories such as raw/, processed/, interim/, and external/ to clarify the data processing pipeline.
- **! PAP001**: Found paper-related files: paper/, paper\main.tex, results\table_results.tex.
- **! PAP003**: README references non-existent directories: data/raw.
  - Recommendation: Update the README to reference directories that exist, or create the missing directories.
- **! PAP004**: CITATION.cff repository-code URL name 'transformer-reproduction' does not match repo directory name 'realistic_ml_repo'.
- **! PAP005**: No \includegraphics commands found in .tex files.
- **! CI002**: No test files or test configuration found.
  - Recommendation: Add a tests/ directory with unit tests and configure pytest so that others can verify the correctness of your code.
- **! CI004**: No issue or PR templates found.
  - Recommendation: Consider adding issue and pull request templates in .github/ to standardize contributions.
