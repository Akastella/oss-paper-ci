# Evaluation Corpus

The evaluation corpus is a collection of synthetic-but-realistic test repositories designed to validate oss-paper-ci's behavior across diverse repository states.

## Design Principles

1. **Synthetic but Realistic**: Repositories mimic real scientific project structures
2. **Safe by Default**: No scripts are executed during evaluation
3. **Minimal Size**: All fixtures are small (no large files or binaries)
4. **Well-Documented**: Each fixture explains its purpose and expected behavior
5. **Defect-Focused**: Each fixture tests specific reproducibility issues

## Repository List

### Python Repositories

#### python_good_repro
A well-structured Python project with good reproducibility practices:
- Complete README with project description
- requirements.txt with pinned dependencies
- reproducibility.yml configuration
- Documented data directory
- Valid results with metrics

**Expected:** High score, status "good", no major findings

#### python_missing_data
Python project missing data documentation:
- Has scripts and environment files
- Missing data/README.md
- Missing data availability statement

**Expected:** Medium score, "needs-work" status, "missing_data_documentation" finding

#### python_missing_environment
Python project missing environment specification:
- Has scripts and data documentation
- Missing requirements.txt or pyproject.toml

**Expected:** Medium score, "needs-work" status, environment-related findings

#### python_bad_results
Python project with invalid results:
- Valid structure otherwise
- results/metrics.json contains invalid JSON

**Expected:** Lower score, "needs-work" status, result validation findings

### Multi-Language Repositories

#### r_repro_project
R project with:
- DESCRIPTION file
- renv.lock for dependency management
- Analysis scripts in R

**Expected:** R ecosystem detected, reasonable score

#### julia_project
Julia project with:
- Project.toml and Manifest.toml
- Julia analysis scripts

**Expected:** Julia ecosystem detected

#### node_analysis_project
Node.js project with:
- package.json and package-lock.json
- JavaScript analysis scripts

**Expected:** Node ecosystem detected

#### make_workflow_project
Make-based workflow with:
- Makefile with reproduce target
- Shell scripts

**Expected:** Make ecosystem detected

#### snakemake_project
Snakemake workflow with:
- Snakefile
- Configuration files

**Expected:** Snakemake ecosystem detected

#### cpp_build_project
C++ project with:
- CMakeLists.txt
- Source files
- Build documentation

**Expected:** C++ ecosystem detected

### Special-Purpose Repositories

#### unsafe_script_project
Tests dry-run detection of risky commands:
- Contains scripts with curl|bash patterns
- Contains scripts with eval() calls
- **NOT executed** during evaluation

**Expected:** Risk detection findings, no execution

#### adoption_before_after
Before/after adoption comparison:
- before/: Minimal repo without reproducibility files
- after/: Scaffolded with complete reproducibility setup

**Expected:** After state shows improvement in score and findings

## Adding New Fixtures

To add a new evaluation fixture:

1. Create a directory under `examples/evaluation-corpus/`
2. Add a README.md explaining the fixture
3. Include synthetic source files (minimal, no real computation)
4. Add an entry in `expected_outcomes.yml`
5. Run evaluation to verify behavior
6. Update golden files if needed

## File Size Limits

- Maximum individual file size: 10KB
- No binary files allowed
- No real data files (use small synthetic samples)
- No external dependencies that require download
