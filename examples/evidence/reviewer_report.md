# Unified Evidence Report

**Repository:** `demo-paper-repo`
**Profile:** reviewer
**Tool:** oss-paper-ci v3.0.0rc1

## Summary

| Metric | Value |
|--------|-------|
| Readiness Score | 91/100 |
| Status | PASS |
| Risk Level | LOW |
| Total Findings | 22 |

> The repository scores 91/100 on reproducibility readiness (status: pass). 22 finding(s) were identified. 3 data documentation check(s) are missing. This is an engineering completeness indicator. It does not judge scientific correctness.

## Reproducibility Scan

- **Score:** 91/100
- **Status:** pass
- **Checks:** 24 pass, 19 warn, 0 fail

## Data Diagnostics

- **Total checks:** 8
- **Missing:** 3

## Result Validation

- **Total checks:** 3
- **Missing:** 0
- **Invalid:** 0

## Ecosystems

- **Python** (python): native

## Trust & Security

- **High findings:** 0
- **Medium findings:** 0
- **Low findings:** 0

## Adoption Suggestions

- `oss-paper-ci.yml`

## Findings

| ID | Severity | Category | Title |
|----|----------|----------|-------|
| `META003` | warning | reproducibility | Citation information exists |
| `META004` | warning | reproducibility | Reproduction instructions exist |
| `META005` | info | reproducibility | Contributing guidelines exist |
| `META006` | info | reproducibility | Version or release information |
| `ENV002` | warning | reproducibility | Lock file exists |
| `ENV003` | warning | reproducibility | Python version specified |
| `ENV006` | warning | reproducibility | Multiple environment files consistent |
| `EXP005` | info | reproducibility | Random seed setting detected |
| `EXP006` | warning | reproducibility | Configuration files exist |
| `EXP007` | info | reproducibility | Notebook risk assessment |
| `DATA002` | warning | reproducibility | Data download instructions exist |
| `DATA003` | info | reproducibility | Data categories distinguished |
| `DATA005` | info | reproducibility | Data paths in .gitignore |
| `RES005` | info | reproducibility | Result regeneration instructions |
| `PAP001` | info | reproducibility | Paper directory detected |
| `PAP004` | info | reproducibility | Citation keys consistent |
| `PAP005` | info | reproducibility | Figure paths in paper match files |
| `CI002` | warning | reproducibility | Tests exist |
| `CI004` | warning | reproducibility | Issue or PR templates exist |
| `DATA_AVAILABILITY` | warning | data | Data availability statement |
| ... | ... | ... | *2 more* |

## Recommended Next Steps

1. Review the evidence map to understand what documentation is present or missing.
2. Check the risk register for known gaps in the repository.
3. Verify that the claimed results trace to data and code.

## Limitations

- This report is an engineering completeness assessment, not a scientific correctness proof.
- A high score does not guarantee the research is correct or reproducible.
- A low score does not mean the research is flawed.
- This tool does not execute experiments unless explicitly requested with --execute.
- Trust and security checks are local static analysis only.
- Dependency inventory is based on declared metadata, not resolved lockfiles.
- This report does not predict paper acceptance or rejection.
