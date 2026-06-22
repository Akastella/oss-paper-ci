# Autoplan Config Diff

**Old:** `tests/fixtures/intake_existing_reproducibility_repo/reproducibility.yml`
**New:** `examples/intake/python_candidate_reproducibility.yml`

## Changed
- **artifacts**
  - Old: `[{'path': 'results/metrics.json', 'type': 'metrics'}]`
  - New: `[{'path': 'results\\metrics.json', 'type': 'metrics'}]`
- **commands**
  - Old: `[{'id': 'train', 'run': 'python scripts/train.py', 'timeout_seconds': 300, 'expected_artifacts': ['results/metrics.json']}]`
  - New: `[{'expected_artifacts': ['results\\metrics.json'], 'id': 'train', 'run': 'python scripts/train.py --epochs 10', 'timeout_seconds': 300}, {'expected_artifacts': ['results\\metrics.json'], 'id': 'evaluate', 'run': 'python scripts/evaluate.py --data data/test.csv', 'timeout_seconds': 300}, {'id': 'cmd', 'run': 'train', 'timeout_seconds': 300}, {'id': 'cmd_2', 'run': 'evaluate', 'timeout_seconds': 300}]`
- **confidence**
  - Old: `0.75`
  - New: `0.87`
