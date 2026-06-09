# Benchmark Fixture Matrix

Generated from test fixtures using the `default` profile.


| Fixture | Language | Status | Score | Blocking | Important | Advisory | Description |
|---------|----------|--------|-------|----------|-----------|----------|-------------|
| minimal_bad_repo | Python | fail | 29 | 4 | 0 | 39 | Minimal repo with almost nothing |
| broken_paper_repo | Python | fail | 75 | 1 | 0 | 42 | Paper repo with broken structure |
| paper_ready_repo | Python | pass | 97 | 0 | 0 | 43 | Well-structured paper repo |
| realistic_ml_repo | Python | pass | 93 | 0 | 0 | 47 | Realistic ML project |
| r_ready_repo | R | fail | 73 | 2 | 0 | 41 | R-based paper repo |
| julia_ready_repo | Julia | fail | 51 | 3 | 0 | 40 | Julia-based paper repo |
| matlab_minimal_repo | MATLAB | fail | 48 | 3 | 0 | 40 | MATLAB-based paper repo |
| make_snakemake_repo | Python/Snakemake | fail | 58 | 2 | 0 | 41 | Snakemake workflow repo |
| demo-paper-repo | Python | pass | 91 | 0 | 0 | 43 | Example paper repo |

## Notes

- Scores and statuses are from the `default` profile
- Different profiles will produce different results
- The matrix verifies scoring consistency across releases
