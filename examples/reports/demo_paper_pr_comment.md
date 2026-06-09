## Reproducibility Report

**Score:** 91/100
**Status:** pass
**Checks:** 0 pass, 16 warn, 4 fail

### Findings (showing 10 of 19)

- **! META003**: No citation information found.
  - Recommendation: Add a CITATION.cff file or a 'Citation' section to your README so that users know how to properly cite your work.
- **! META004**: No reproduction instructions found in README.
  - Recommendation: Add sections such as 'Getting Started', 'Installation', or 'Usage' to your README so that others can reproduce your results.
- **! META005**: No contributing guidelines found.
  - Recommendation: Consider adding a CONTRIBUTING.md file or an issue template to encourage community contributions.
- **! META006**: No version or release information found.
  - Recommendation: Add a CHANGELOG, VERSION file, or a version field in pyproject.toml so users can track releases.
- **! ENV002**: No lock file found
  - Recommendation: Add a lock file (e.g. poetry.lock, Pipfile.lock, uv.lock, or conda-lock.yml) to ensure reproducible dependency resolution.
- **! ENV003**: No Python version specification found
  - Recommendation: Specify the required Python version in pyproject.toml (requires-python), setup.cfg (python_requires), .python-version, or Pipfile.
- **! ENV006**: Both requirements.txt and environment.yml exist but no clear guidance found in README
  - Recommendation: Document in the README which file (requirements.txt or environment.yml) users should use and under what circumstances.
- **! EXP005**: No random seed setting detected in scripts/ or src/.
  - Recommendation: Set random seeds (e.g., random.seed(), np.random.seed(), torch.manual_seed()) so experiments are reproducible.
- **! EXP006**: No configuration files or CLI argument parsing found.
  - Recommendation: Add a config file (e.g., config.yaml) or use argparse/click so experiment parameters are explicit and reproducible.
- **! EXP007**: No Jupyter notebooks found in the repository.
