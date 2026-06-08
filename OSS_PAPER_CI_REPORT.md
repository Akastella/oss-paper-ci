# 🔬 oss-paper-ci Report

**Score: 92/100** ⚠️

| Metric | Count |
|--------|-------|
| Errors | 4 |
| Warnings | 15 |
| Info | 22 |

## ⚠️ Warnings

- **META003**: No citation information found.
- **ENV002**: No lock file found
- **DATA002**: No data download instructions found.
- **DATA003**: No distinction between data categories found.
- **DATA005**: No data-related patterns found in .gitignore.
- **RES001**: No results directories found.
- **RES004**: 1 unreferenced image(s) found: tests\fixtures\paper_ready_repo\figures\results.png.
- **RES005**: No result regeneration instructions found.
- **PAP001**: Found paper-related files: tests\fixtures\paper_ready_repo\paper\main.tex.
- **PAP004**: No citation files found to verify.
- **PAP005**: All 1 figure reference(s) resolve.
- **CI004**: No issue or PR templates found.

## 📋 Check Details

| ID | Title | Status | Severity |
|----|-------|--------|----------|
| META001 | README file exists | ✅ pass | ❌ error |
| META002 | LICENSE file exists | ✅ pass | ❌ error |
| META003 | Citation information exists | ⚠️ warn | ⚠️ warning |
| META004 | Reproduction instructions exist | ✅ pass | ⚠️ warning |
| META005 | Contributing guidelines exist | ✅ pass | ℹ️ info |
| META006 | Version or release information | ✅ pass | ℹ️ info |
| META007 | Artifact metadata file exists | ✅ pass | ℹ️ info |
| ENV001 | Environment specification file exists | ✅ pass | ❌ error |
| ENV002 | Lock file exists | ⚠️ warn | ⚠️ warning |
| ENV003 | Python version specified | ✅ pass | ⚠️ warning |
| ENV004 | System dependencies documented | ✅ pass | ℹ️ info |
| ENV005 | GPU/CPU requirements documented | ✅ pass | ℹ️ info |
| ENV006 | Multiple environment files consistent | ✅ pass | ⚠️ warning |
| EXP001 | Experiment entry points exist | ✅ pass | ❌ error |
| EXP002 | One-command reproduction script exists | ✅ pass | ⚠️ warning |
| EXP003 | Smoke test or quickstart exists | ✅ pass | ℹ️ info |
| EXP004 | Long vs short experiment distinction | ✅ pass | ℹ️ info |
| EXP005 | Random seed setting detected | ✅ pass | ℹ️ info |
| EXP006 | Configuration files exist | ✅ pass | ℹ️ info |
| DATA001 | Data source documentation exists | ✅ pass | ⚠️ warning |
| DATA002 | Data download instructions exist | ⚠️ warn | ⚠️ warning |
| DATA003 | Data categories distinguished | ⚠️ warn | ℹ️ info |
| DATA004 | Large files not in repository | ✅ pass | ⚠️ warning |
| DATA005 | Data paths in .gitignore | ⚠️ warn | ℹ️ info |
| DATA006 | Privacy and licensing for data | ✅ pass | ℹ️ info |
| RES001 | Results directory exists | ⚠️ warn | ⚠️ warning |
| RES002 | Figures referenced in README exist | ✅ pass | ⚠️ warning |
| RES003 | Results have generation scripts | ✅ pass | ℹ️ info |
| RES004 | No orphan figures | ⚠️ warn | ℹ️ info |
| RES005 | Result regeneration instructions | ⚠️ warn | ℹ️ info |
| PAP001 | Paper directory detected | ⚠️ warn | ℹ️ info |
| PAP002 | README commands match existing scripts | ✅ pass | ⚠️ warning |
| PAP003 | README directory references exist | ✅ pass | ⚠️ warning |
| PAP004 | Citation keys consistent | ⚠️ warn | ℹ️ info |
| PAP005 | Figure paths in paper match files | ⚠️ warn | ℹ️ info |
| CI001 | GitHub Actions workflows exist | ✅ pass | ℹ️ info |
| CI002 | Tests exist | ✅ pass | ⚠️ warning |
| CI003 | Linting or formatting configured | ✅ pass | ℹ️ info |
| CI004 | Issue or PR templates exist | ⚠️ warn | ⚠️ warning |
| CI005 | Security policy exists | ✅ pass | ℹ️ info |
| CI006 | Package metadata complete | ✅ pass | ℹ️ info |

## 🔍 Evidence & Recommendations

### META003: Citation information exists

**Finding:** No citation information found.

**Recommendation:** Add a CITATION.cff file or a 'Citation' section to your README so that users know how to properly cite your work.

### ENV002: Lock file exists

**Finding:** No lock file found

**Recommendation:** Add a lock file (e.g. poetry.lock, Pipfile.lock, uv.lock, or conda-lock.yml) to ensure reproducible dependency resolution.

### DATA002: Data download instructions exist

**Finding:** No data download instructions found.

**Recommendation:** Add download instructions to your README (e.g. wget/curl commands, links to Zenodo/Figshare/HuggingFace) or include a download_data.sh / get_data.py script.

### DATA003: Data categories distinguished

**Finding:** No distinction between data categories found.

**Recommendation:** Consider organizing your data into subdirectories such as raw/, processed/, interim/, and external/ to clarify the data processing pipeline.

### DATA005: Data paths in .gitignore

**Finding:** No data-related patterns found in .gitignore.

**Recommendation:** Add data patterns to .gitignore (e.g. data/, *.csv, *.h5, *.parquet) to prevent accidental commits of large or sensitive data files.

### RES001: Results directory exists

**Finding:** No results directories found.

**Recommendation:** Create a results directory (e.g. results/, output/, figures/) to store experiment outputs so reviewers can inspect them.

### RES004: No orphan figures

**Finding:** 1 unreferenced image(s) found: tests\fixtures\paper_ready_repo\figures\results.png.

**Evidence:**
- `tests\fixtures\paper_ready_repo\figures\results.png`

**Recommendation:** Remove unused image files or reference them in your README, paper, or scripts to keep the repository clean.

### RES005: Result regeneration instructions

**Finding:** No result regeneration instructions found.

**Recommendation:** Add instructions to your README (e.g. 'To reproduce Figure 1, run ...') or a Makefile with result-related targets so others can regenerate your results.

### PAP001: Paper directory detected

**Finding:** Found paper-related files: tests\fixtures\paper_ready_repo\paper\main.tex.

**Evidence:**
- `tests\fixtures\paper_ready_repo\paper\main.tex`

### PAP004: Citation keys consistent

**Finding:** No citation files found to verify.

**Recommendation:** Add a CITATION.cff or .bib file so that users can properly cite your work.

### PAP005: Figure paths in paper match files

**Finding:** All 1 figure reference(s) resolve.

**Evidence:**
- `main.tex: ../figures/results.png`

### CI004: Issue or PR templates exist

**Finding:** No issue or PR templates found.

**Recommendation:** Consider adding issue and pull request templates in .github/ to standardize contributions.

---

> **Disclaimer:** This tool evaluates repository *reproducibility readiness*, not paper quality, correctness, novelty, or likelihood of acceptance. A high score does not guarantee reproducibility; a low score does not mean the research is flawed. It is a checklist for engineering completeness.

*Generated by oss-paper-ci v0.1.0*