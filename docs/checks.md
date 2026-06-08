# Check Reference

Complete reference for all reproducibility checks performed by oss-paper-ci.

Each check has the following fields:

| Field       | Description                                           |
|-------------|-------------------------------------------------------|
| ID          | Unique identifier (e.g. META001)                      |
| Category    | Group the check belongs to (e.g. META, ENV, EXP)      |
| Severity    | Impact level: error, warning, or info                 |

## Metadata (META)

### META001 -- README file exists

| Field      | Value   |
|------------|---------|
| ID         | META001 |
| Category   | META    |
| Severity   | error   |

**What it checks:** Looks for `README.md`, `README.rst`, or `README` in the repo root.

**Pass:** Any of these files exists.
**Fail:** None found.

**Recommendation:** Add a README.md to your repository so that others can understand and reproduce your work.

---

### META002 -- LICENSE file exists

| Field      | Value   |
|------------|---------|
| ID         | META002 |
| Category   | META    |
| Severity   | error   |

**What it checks:** Looks for `LICENSE`, `LICENSE.md`, `LICENSE.txt`, `LICENCE`, or `COPYING`.

**Pass:** Any license file found.
**Fail:** None found.

**Recommendation:** Add a LICENSE file to clarify the terms under which your code and data may be reused.

---

### META003 -- Citation information exists

| Field      | Value   |
|------------|---------|
| ID         | META003 |
| Category   | META    |
| Severity   | warning |

**What it checks:** Looks for `CITATION.cff`, `CITATION`, `CITATION.bib`, or a citation section (heading matching "cite", "citation", "how to cite", "referencing") in the README.

**Pass:** Citation file or section found.
**Warn:** No citation information found.

**Recommendation:** Add a CITATION.cff file or a "Citation" section to your README.

---

### META004 -- Reproduction instructions exist

| Field      | Value   |
|------------|---------|
| ID         | META004 |
| Category   | META    |
| Severity   | warning |

**What it checks:** Searches the README for keywords: "reproduc", "getting started", "quickstart", "installation", "usage".

**Pass:** At least one keyword found in README.
**Warn:** None found.

**Recommendation:** Add sections such as "Getting Started", "Installation", or "Usage" to your README.

---

### META005 -- Contributing guidelines exist

| Field      | Value   |
|------------|---------|
| ID         | META005 |
| Category   | META    |
| Severity   | info    |

**What it checks:** Looks for `CONTRIBUTING.md`, `CONTRIBUTING`, `.github/ISSUE_TEMPLATE`, `docs/contributing.md`, `docs/contributing.rst`, or `docs/contributing`.

**Pass:** Any contributing file found.
**Info:** None found.

**Recommendation:** Consider adding a CONTRIBUTING.md file or an issue template to encourage community contributions.

---

### META006 -- Version or release information

| Field      | Value   |
|------------|---------|
| ID         | META006 |
| Category   | META    |
| Severity   | info    |

**What it checks:** Looks for `CHANGELOG.md`, `CHANGELOG`, `CHANGES`, `CHANGES.md`, `HISTORY`, `HISTORY.md`, `VERSION`, `VERSION.txt`, or a `version` field in `pyproject.toml`.

**Pass:** Version/release file found.
**Info:** None found.

**Recommendation:** Add a CHANGELOG or VERSION file so users can track releases.

---

### META007 -- Artifact metadata file exists

| Field      | Value   |
|------------|---------|
| ID         | META007 |
| Category   | META    |
| Severity   | info    |

**What it checks:** Looks for `oss-paper-ci.yml`, `artifact.yml`, `reproducibility.yml`, or `.reproducibility.yml`.

**Pass:** Any metadata file found.
**Info:** None found.

**Recommendation:** Add an artifact metadata file to describe how to reproduce your experiments.

---

## Environment (ENV)

### ENV001 -- Environment specification file exists

| Field      | Value   |
|------------|---------|
| ID         | ENV001 |
| Category   | ENV     |
| Severity   | error   |

**What it checks:** Looks for any of: `requirements.txt`, `environment.yml`, `environment.yaml`, `pyproject.toml`, `Pipfile`, `poetry.lock`, `setup.py`, `setup.cfg`, `Dockerfile`, `container.def`, `Singularity`, `apt.txt`, `install.R`, `renv.lock`.

**Pass:** At least one file found.
**Fail:** None found.

**Recommendation:** Add an environment specification file such as requirements.txt, pyproject.toml, environment.yml, or a Dockerfile.

---

### ENV002 -- Lock file exists

| Field      | Value   |
|------------|---------|
| ID         | ENV002 |
| Category   | ENV     |
| Severity   | warning |

**What it checks:** Looks for `poetry.lock`, `Pipfile.lock`, `conda-lock.yml`, `uv.lock`, or `requirements.txt` with pinned versions (`==`).

**Pass:** Lock file or pinned requirements found.
**Warn:** No lock file found.

**Recommendation:** Add a lock file to ensure reproducible dependency resolution.

---

### ENV003 -- Python version specified

| Field      | Value   |
|------------|---------|
| ID         | ENV003 |
| Category   | ENV     |
| Severity   | warning |

**What it checks:** Looks for `requires-python` in `pyproject.toml`, `python_requires` in `setup.cfg`, `runtime.txt`, `.python-version`, `python_version` in `Pipfile`, or a Python version mention (e.g., "Python 3.11") in README.

**Pass:** Python version specified somewhere.
**Warn:** No specification found.

**Recommendation:** Specify the required Python version in pyproject.toml, setup.cfg, .python-version, or Pipfile.

---

### ENV004 -- System dependencies documented

| Field      | Value   |
|------------|---------|
| ID         | ENV004 |
| Category   | ENV     |
| Severity   | info    |

**What it checks:** Looks for `apt.txt`, `Brewfile`, `install.sh`, or system dependency keywords (apt, brew, sudo, install, prerequisite, dependency, system, apt-get, yum) in the README.

**Pass:** System dependency documentation found.
**Info:** Not found.

**Recommendation:** Document system-level prerequisites in the README or a dedicated file.

---

### ENV005 -- GPU/CPU requirements documented

| Field      | Value   |
|------------|---------|
| ID         | ENV005 |
| Category   | ENV     |
| Severity   | info    |

**What it checks:** Searches README for hardware keywords: GPU, CUDA, cpu, gpu, TPU, hardware, memory, RAM.

**Pass:** Hardware requirements mentioned.
**Info:** Not mentioned.

**Recommendation:** If the project requires specific hardware, document these requirements in the README.

---

### ENV006 -- Multiple environment files consistent

| Field      | Value   |
|------------|---------|
| ID         | ENV006 |
| Category   | ENV     |
| Severity   | warning |

**What it checks:** If both `requirements.txt` and `environment.yml`, or both `pyproject.toml` and `requirements.txt` exist, checks whether the README mentions both and provides guidance.

**Pass:** Only one env file pair exists, or README explains the choice.
**Warn:** Conflicting files exist with no guidance.

**Recommendation:** Document in the README which file users should use and under what circumstances.

---

## Experiments (EXP)

### EXP001 -- Experiment entry points exist

| Field      | Value   |
|------------|---------|
| ID         | EXP001 |
| Category   | EXP     |
| Severity   | error   |

**What it checks:** Looks for directories `scripts/`, `experiments/`, `src/`, `notebooks/` or files `train.py`, `eval.py`, `run.py`, `run_experiment.py`, `main.py`, `Makefile`.

**Pass:** At least one entry point found.
**Fail:** None found.

**Recommendation:** Add a scripts/, experiments/, or src/ directory, or a top-level entry-point script.

---

### EXP002 -- One-command reproduction script exists

| Field      | Value   |
|------------|---------|
| ID         | EXP002 |
| Category   | EXP     |
| Severity   | warning |

**What it checks:** Looks for `run.sh`, `run_all.sh`, `reproduce.sh`, `Makefile`, `justfile`, `run_experiments.py`. Also checks README for run/reproduce/quickstart sections with code blocks.

**Pass:** Dedicated script found, or README has a run section with code blocks.
**Warn:** No clear single-command path.

**Recommendation:** Add a run.sh or Makefile that reproduces the main results, or document a single command in the README.

---

### EXP003 -- Smoke test or quickstart exists

| Field      | Value   |
|------------|---------|
| ID         | EXP003 |
| Category   | EXP     |
| Severity   | info    |

**What it checks:** Looks for `quick_start.py`, `smoke_test.py`, `test_run.sh`, `demo.py`, `example.py`. Also searches README for "quick", "demo", "example", "test run", "fast".

**Pass:** Quickstart file or reference found.
**Warn:** Not found.

**Recommendation:** Add a quick_start.py or short demo so users can verify setup works.

---

### EXP004 -- Long vs short experiment distinction

| Field      | Value   |
|------------|---------|
| ID         | EXP004 |
| Category   | EXP     |
| Severity   | info    |

**What it checks:** Searches README, Python files, and config files for keywords: quick, fast, full, long, short, demo, subset.

**Pass:** Mode distinction found.
**Warn:** Not found.

**Recommendation:** Document how to run a quick sanity-check experiment vs. the full experiment.

---

### EXP005 -- Random seed setting detected

| Field      | Value   |
|------------|---------|
| ID         | EXP005 |
| Category   | EXP     |
| Severity   | info    |

**What it checks:** Searches Python files for patterns like `seed=42`, `random.seed(`, `np.random.seed(`, `torch.manual_seed(`, `set_seed(`, `tf.random.set_seed(`, `RANDOM_SEED`, `SEED=42`. Falls back to README keywords.

**Pass:** Seed-setting code or documentation found.
**Warn:** Not found.

**Recommendation:** Set random seeds so experiments are reproducible.

---

### EXP006 -- Configuration files exist

| Field      | Value   |
|------------|---------|
| ID         | EXP006 |
| Category   | EXP     |
| Severity   | info    |

**What it checks:** Looks for config files (`config.yaml`, `config.yml`, `.env`, `hydra.yaml`, `params.yaml`, etc.), config directories (`conf/`, `config/`, `configs/`, `settings/`), or argument parsing (`argparse`, `click`, `typer`) in Python files.

**Pass:** Configuration mechanism found.
**Warn:** Not found.

**Recommendation:** Add a config file or use argparse/click so experiment parameters are explicit and reproducible.

---

## Data (DATA)

### DATA001 -- Data source documentation exists

| Field      | Value   |
|------------|---------|
| ID         | DATA001 |
| Category   | DATA    |
| Severity   | warning |

**What it checks:** Searches README for "data", "dataset", "download", "data source". Also checks for `data/` directory or dedicated files like `DATASET.md`, `data/README.md`.

**Pass:** Data documentation found.
**Warn:** Not found.

**Recommendation:** Add data-related information to your README or create a dedicated data/README file.

---

### DATA002 -- Data download instructions exist

| Field      | Value   |
|------------|---------|
| ID         | DATA002 |
| Category   | DATA    |
| Severity   | warning |

**What it checks:** Searches README for download tool keywords (wget, curl, gdown, kaggle, huggingface, zenodo, figshare) and data URLs. Also checks for download scripts (`download_data.sh`, `get_data.py`).

**Pass:** Download instructions or scripts found.
**Warn:** Not found.

**Recommendation:** Add download instructions or include a download_data.sh / get_data.py script.

---

### DATA003 -- Data categories distinguished

| Field      | Value   |
|------------|---------|
| ID         | DATA003 |
| Category   | DATA    |
| Severity   | info    |

**What it checks:** Looks for `data/raw/`, `data/processed/`, `data/interim/`, `data/external/` directories, or README keywords "raw data", "processed data", "intermediate".

**Pass:** Data categories found.
**Info:** Not found.

**Recommendation:** Organize data into subdirectories such as raw/, processed/, interim/.

---

### DATA004 -- Large files not in repository

| Field      | Value   |
|------------|---------|
| ID         | DATA004 |
| Category   | DATA    |
| Severity   | warning |

**What it checks:** Scans for large binary files (`.h5`, `.pkl`, `.npy`, `.parquet`, `.zip`, `.tar`, `.gz`) and CSV files over 1 MB. Checks for Git LFS config or `.gitignore` patterns.

**Pass:** No large files found, or LFS/gitignore configured.
**Warn:** Large files found without LFS or gitignore protection.

**Recommendation:** Use Git LFS or add large file extensions to .gitignore.

---

### DATA005 -- Data paths in .gitignore

| Field      | Value   |
|------------|---------|
| ID         | DATA005 |
| Category   | DATA    |
| Severity   | info    |

**What it checks:** Searches `.gitignore` for data-related patterns (`data/`, `*.csv`, `*.h5`, `*.parquet`, etc.).

**Pass:** Data patterns found in .gitignore.
**Info:** Not found.

**Recommendation:** Add data patterns to .gitignore to prevent accidental commits.

---

### DATA006 -- Privacy and licensing for data

| Field      | Value   |
|------------|---------|
| ID         | DATA006 |
| Category   | DATA    |
| Severity   | info    |

**What it checks:** Searches README for privacy/licensing keywords (license, privacy, public, synthetic, anonymized, consent). Checks for `DATA_LICENSE` files.

**Pass:** Privacy/licensing information found.
**Info:** Not found.

**Recommendation:** Add information about data licensing, privacy, or usage terms.

---

## Results (RES)

### RES001 -- Results directory exists

| Field      | Value   |
|------------|---------|
| ID         | RES001 |
| Category   | RES     |
| Severity   | warning |

**What it checks:** Looks for `results/`, `output/`, `figures/`, `plots/`, `tables/`, `logs/`, `artifacts/` directories.

**Pass:** Results directory found.
**Warn:** Not found.

**Recommendation:** Create a dedicated directory for experiment outputs and figures.

---

### RES002 -- Figures referenced in README exist

| Field      | Value   |
|------------|---------|
| ID         | RES002 |
| Category   | RES     |
| Severity   | warning |

**What it checks:** Parses Markdown image references (`![alt](path)`) and HTML `<img>` tags in the README. Verifies that referenced local image files actually exist in the repository.

**Pass:** All referenced figures exist, or no figure references found.
**Warn:** Some referenced figures are missing.

**Recommendation:** Ensure all images referenced in the README are committed to the repository, or update broken references.

---

### RES003 -- Results have generation scripts

| Field      | Value   |
|------------|---------|
| ID         | RES003 |
| Category   | RES     |
| Severity   | info    |

**What it checks:** If a results directory exists, looks for Python scripts in `scripts/` or `src/` whose names start with `plot`, `generate`, `make_figure`, or `visualize`. Also checks Makefile for result-related targets.

**Pass:** Generation scripts found.
**Info:** No generation scripts found.

**Recommendation:** Add scripts (e.g. plot_*.py, generate_*.py) that produce your figures and tables so results can be regenerated.

---

### RES004 -- No orphan figures

| Field      | Value   |
|------------|---------|
| ID         | RES004 |
| Category   | RES     |
| Severity   | info    |

**What it checks:** Collects all image files (`.png`, `.jpg`, `.jpeg`, `.svg`, `.pdf`, `.eps`) in the repository and checks whether each is referenced in the README, paper/, or scripts/ files.

**Pass:** All image files are referenced somewhere.
**Info:** Some image files are not referenced.

**Recommendation:** Remove unused image files or reference them in your README, paper, or scripts to keep the repository clean.

---

### RES005 -- Result regeneration instructions

| Field      | Value   |
|------------|---------|
| ID         | RES005 |
| Category   | RES     |
| Severity   | info    |

**What it checks:** Searches README for regeneration keywords ("regenerat", "re-run", "rerun", "reproduce figure/table/result"). Checks Makefile for result-related targets.

**Pass:** Regeneration instructions found.
**Info:** Not found.

**Recommendation:** Add instructions to your README (e.g. 'To reproduce Figure 1, run ...') or a Makefile with result-related targets so others can regenerate your results.

---

## Paper-Code (PAP)

### PAP001 -- Paper directory detected

| Field      | Value   |
|------------|---------|
| ID         | PAP001 |
| Category   | PAP     |
| Severity   | info    |

**What it checks:** Looks for `paper/`, `manuscript/`, `latex/`, `tex/`, `docs/paper/` directories or `.tex` files in the root.

**Pass:** Paper directory or .tex files found.
**Info:** Not found.

**Recommendation:** If your project includes a paper, consider placing it in a paper/, manuscript/, or latex/ directory.

---

### PAP002 -- README commands match existing scripts

| Field      | Value   |
|------------|---------|
| ID         | PAP002 |
| Category   | PAP     |
| Severity   | warning |

**What it checks:** Parses code blocks in the README and extracts script paths from commands (e.g., `python train.py`, `bash run.sh`). Verifies that each referenced script file actually exists in the repository.

**Pass:** All referenced scripts exist, or no script references found.
**Warn:** Some referenced scripts are missing.

**Recommendation:** Update the README commands to reference scripts that exist in the repository, or add the missing scripts.

---

### PAP003 -- README directory references exist

| Field      | Value   |
|------------|---------|
| ID         | PAP003 |
| Category   | PAP     |
| Severity   | warning |

**What it checks:** Extracts directory-like references (paths ending with `/`) from the README text and verifies that each referenced directory actually exists in the repository.

**Pass:** All referenced directories exist, or no directory references found.
**Warn:** Some referenced directories are missing.

**Recommendation:** Update the README to reference directories that exist, or create the missing directories.

---

### PAP004 -- Citation keys consistent

| Field      | Value   |
|------------|---------|
| ID         | PAP004 |
| Category   | PAP     |
| Severity   | info    |

**What it checks:** If `CITATION.cff` exists, checks that the `repository-code` URL matches the repo directory name and that a `title` field is present. If `.bib` files exist, checks that each is referenced in the README or `.tex` files.

**Pass:** Citation files are present and consistent.
**Info:** No citation files found, or inconsistencies detected.

**Recommendation:** Add a CITATION.cff or .bib file so that users can properly cite your work.

---

### PAP005 -- Figure paths in paper match files

| Field      | Value   |
|------------|---------|
| ID         | PAP005 |
| Category   | PAP     |
| Severity   | info    |

**What it checks:** Extracts `\includegraphics{path}` references from `.tex` files and verifies that each referenced figure file exists. Tries common image extensions if the path has no extension.

**Pass:** All figure references resolve.
**Info:** Some figures are missing, or no `\includegraphics` commands found.

**Recommendation:** Ensure that all figures referenced in LaTeX files are present in the repository.

---

## CI (CI)

### CI001 -- GitHub Actions workflows exist

| Field      | Value   |
|------------|---------|
| ID         | CI001  |
| Category   | CI     |
| Severity   | info   |

**What it checks:** Looks for `.github/workflows/*.yml` or `.github/workflows/*.yaml` files.

**Pass:** GitHub Actions workflow files found.
**Info:** Not found.

**Recommendation:** Add CI configuration to automate testing and reproducibility checks.

---

### CI002 -- Tests exist

| Field      | Value   |
|------------|---------|
| ID         | CI002   |
| Category   | CI      |
| Severity   | warning |

**What it checks:** Looks for `tests/` or `test/` directories, test files matching `test_*.py` or `*_test.py`, and test config files (`pytest.ini`, `conftest.py`, `tox.ini`). Checks `pyproject.toml` for `[tool.pytest]` section.

**Pass:** Test infrastructure found.
**Warn:** No test files or configuration found.

**Recommendation:** Add a tests/ directory with unit tests and configure pytest so that others can verify the correctness of your code.

---

### CI003 -- Linting or formatting configured

| Field      | Value   |
|------------|---------|
| ID         | CI003  |
| Category   | CI     |
| Severity   | info   |

**What it checks:** Looks for `.flake8`, `.pylintrc`, `.pre-commit-config.yaml`, `.editorconfig`, `ruff.toml`, or linting tool sections in `pyproject.toml` (`[tool.ruff]`, `[tool.black]`, `[tool.isort]`, `[tool.flake8]`, `[tool.pylint]`, `[tool.mypy]`).

**Pass:** Linting/formatting configuration found.
**Info:** Not found.

**Recommendation:** Add linting configuration to maintain code quality.

---

### CI004 -- Issue or PR templates exist

| Field      | Value   |
|------------|---------|
| ID         | CI004  |
| Category   | CI     |
| Severity   | info   |

**What it checks:** Looks for `.github/ISSUE_TEMPLATE/` directory contents, `.github/PULL_REQUEST_TEMPLATE.md`, or `.github/ISSUE_TEMPLATE.md`.

**Pass:** Issue or PR templates found.
**Warn:** Not found.

**Recommendation:** Consider adding issue and pull request templates in .github/ to standardize contributions.

---

### CI005 -- Security policy exists

| Field      | Value   |
|------------|---------|
| ID         | CI005  |
| Category   | CI     |
| Severity   | info   |

**What it checks:** Looks for `SECURITY.md`, `SECURITY`, `.github/SECURITY.md`, or `security.md`.

**Pass:** Security policy found.
**Info:** Not found.

**Recommendation:** Consider adding a SECURITY.md file to describe how users should report security vulnerabilities.

---

### CI006 -- Package metadata complete

| Field      | Value   |
|------------|---------|
| ID         | CI006  |
| Category   | CI     |
| Severity   | info   |

**What it checks:** Checks `pyproject.toml` or `setup.py`/`setup.cfg` for required fields: name, version, description, license, authors.

**Pass:** All required fields present.
**Info:** Some fields missing, or no package metadata files found.

**Recommendation:** Add a pyproject.toml (or setup.py/setup.cfg) with name, version, description, license, and authors fields.
