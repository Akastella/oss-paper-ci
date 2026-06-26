# Execution Plan

**Executable:** Yes
**Dry run:** True
**Total timeout:** 900s
**Parallel groups:** 4
**Steps:** 4

- Ready: 4
- Blocked: 0
- Skipped: 0

## DAG Summary

- **Topological order:** `preprocess -> train -> evaluate -> visualize`
- **Critical path:** `preprocess -> train -> evaluate -> visualize`
- **Critical path duration:** 900s

## Steps

| # | Step ID | Status | Parallel Group | Timeout | Dependencies |
|---|---------|--------|----------------|---------|--------------|
| 1 | `preprocess` | ready | 0 | 120s | `-` |
| 2 | `train` | ready | 1 | 600s | `preprocess` |
| 3 | `evaluate` | ready | 2 | 120s | `train` |
| 4 | `visualize` | ready | 3 | 60s | `evaluate` |

## Safety

- **Level:** safe
- **Blocked commands:** 0
- **Requires network:** False
- **Requires install:** False
