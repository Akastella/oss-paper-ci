# Reproducibility Dossier

> This dossier is an automated assessment of reproducibility readiness. It does not judge paper quality, correctness, or significance. A high score does not guarantee reproduction. A low score does not mean the research is flawed.

## Executive Summary

Repository reproducibility readiness score: 91/100. The repository passed basic reproducibility readiness checks.

**Status:** Ready | **Score:** 91/100 | **Low:** High

- This section summarizes the reproducibility evidence available in the repository. It does not make accept/reject recommendations.
- This summary does not make accept/reject recommendations. Use your domain expertise and peer review standards.

## Evidence Map

| Category | Item | Status | Why It Matters |
|------|------|--------|------------|
| metadata | README file | Present | A README helps others understand the project. |
| metadata | License | Present | A license clarifies usage rights. |
| metadata | Citation information | Partial | Citation info helps others give proper credit. |
| environment | Dependency file | Present | Dependency files let others install the same environment. |
| environment | Python version | Partial | Specifying Python version prevents compatibility issues. |
| execution | Entry point scripts | Present | Entry points tell others how to run the code. |
| execution | Reproduction contract | Present | A reproducibility.yml declares how to reproduce results. |
| data | Data documentation | Present | Data documentation explains what data is needed. |
| results | Output directories | Present | Output directories show where results are stored. |
| automation | CI workflow | Present | CI workflows automate reproducibility checks. |

## Remediation Plan

### [P1] Add a CITATION.cff file or a 'Citation' section to your README so that users know how to properly cite your work.

**Rationale:** Check META003 reported: No citation information found.

**Verify:** `oss-paper-ci scan .  # check META003`

**Effort:** low

### [P1] Add sections such as 'Getting Started', 'Installation', or 'Usage' to your README so that others can reproduce your results.

**Rationale:** Check META004 reported: No reproduction instructions found in README.

**Verify:** `oss-paper-ci scan .  # check META004`

**Effort:** low

### [P1] Add a lock file (e.g. poetry.lock, Pipfile.lock, uv.lock, or conda-lock.yml) to ensure reproducible dependency resolution.

**Rationale:** Check ENV002 reported: No lock file found

**Verify:** `oss-paper-ci scan .  # check ENV002`

**Effort:** low

### [P1] Specify the required Python version in pyproject.toml (requires-python), setup.cfg (python_requires), .python-version, or Pipfile.

**Rationale:** Check ENV003 reported: No Python version specification found

**Verify:** `oss-paper-ci scan .  # check ENV003`

**Effort:** low

### [P1] Document in the README which file (requirements.txt or environment.yml) users should use and under what circumstances.

**Rationale:** Check ENV006 reported: Both requirements.txt and environment.yml exist but no clear guidance found in README

**Verify:** `oss-paper-ci scan .  # check ENV006`

**Effort:** low

### [P1] Add a config file (e.g., config.yaml) or use argparse/click so experiment parameters are explicit and reproducible.

**Rationale:** Check EXP006 reported: No configuration files or CLI argument parsing found.

**Verify:** `oss-paper-ci scan .  # check EXP006`

**Effort:** low

### [P1] Add download instructions to your README (e.g. wget/curl commands, links to Zenodo/Figshare/HuggingFace) or include a download_data.sh / get_data.py script.

**Rationale:** Check DATA002 reported: No data download instructions found.

**Verify:** `oss-paper-ci scan .  # check DATA002`

**Effort:** low

### [P1] Add a tests/ directory with unit tests and configure pytest so that others can verify the correctness of your code.

**Rationale:** Check CI002 reported: No test files or test configuration found.

**Verify:** `oss-paper-ci scan .  # check CI002`

**Effort:** low

### [P1] Consider adding issue and pull request templates in .github/ to standardize contributions.

**Rationale:** Check CI004 reported: No issue or PR templates found.

**Verify:** `oss-paper-ci scan .  # check CI004`

**Effort:** low

### [P2] Consider adding a CONTRIBUTING.md file or an issue template to encourage community contributions.

**Rationale:** Check META005 reported: No contributing guidelines found.

**Verify:** `oss-paper-ci scan .  # check META005`

**Effort:** low

### [P2] Add a CHANGELOG, VERSION file, or a version field in pyproject.toml so users can track releases.

**Rationale:** Check META006 reported: No version or release information found.

**Verify:** `oss-paper-ci scan .  # check META006`

**Effort:** low

### [P2] Set random seeds (e.g., random.seed(), np.random.seed(), torch.manual_seed()) so experiments are reproducible.

**Rationale:** Check EXP005 reported: No random seed setting detected in scripts/ or src/.

**Verify:** `oss-paper-ci scan .  # check EXP005`

**Effort:** low

### [P2] Address EXP007: No Jupyter notebooks found in the repository.

**Rationale:** Check EXP007 reported: No Jupyter notebooks found in the repository.

**Verify:** `oss-paper-ci scan .  # check EXP007`

**Effort:** low

### [P2] Consider organizing your data into subdirectories such as raw/, processed/, interim/, and external/ to clarify the data processing pipeline.

**Rationale:** Check DATA003 reported: No distinction between data categories found.

**Verify:** `oss-paper-ci scan .  # check DATA003`

**Effort:** low

### [P2] Add data patterns to .gitignore (e.g. data/, *.csv, *.h5, *.parquet) to prevent accidental commits of large or sensitive data files.

**Rationale:** Check DATA005 reported: No data-related patterns found in .gitignore.

**Verify:** `oss-paper-ci scan .  # check DATA005`

**Effort:** low

### [P2] Add instructions to your README (e.g. 'To reproduce Figure 1, run ...') or a Makefile with result-related targets so others can regenerate your results.

**Rationale:** Check RES005 reported: No result regeneration instructions found.

**Verify:** `oss-paper-ci scan .  # check RES005`

**Effort:** low

### [P2] If your project includes a paper, consider placing it in a paper/, manuscript/, or latex/ directory.

**Rationale:** Check PAP001 reported: No paper or manuscript files detected.

**Verify:** `oss-paper-ci scan .  # check PAP001`

**Effort:** low

### [P2] Add a CITATION.cff or .bib file so that users can properly cite your work.

**Rationale:** Check PAP004 reported: No citation files found to verify.

**Verify:** `oss-paper-ci scan .  # check PAP004`

**Effort:** low

### [P2] Address PAP005: No .tex files found; skipping figure path check.

**Rationale:** Check PAP005 reported: No .tex files found; skipping figure path check.

**Verify:** `oss-paper-ci scan .  # check PAP005`

**Effort:** low

## Next Steps

- Review missing items in the evidence map
- Assess severity in the risk register
- Use the remediation plan to understand what the author can do

## What This Does NOT Mean

- This dossier is an automated assessment of reproducibility readiness. It does not judge paper quality, correctness, or significance. A high score does not guarantee reproduction. A low score does not mean the research is flawed.

---
*Generated by oss-paper-ci*
