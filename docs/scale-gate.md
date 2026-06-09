# Scale Gate

The scale gate is an engineering regression test that verifies batch scanning
works correctly at a small scale.

## Usage

```bash
# Generate synthetic corpus
python scripts/generate_synthetic_corpus.py --count 20 --output tests/fixtures/synthetic_corpus

# Run scale gate
python scripts/scale_gate.py --format markdown --output examples/benchmark/scale.md
python scripts/scale_gate.py --format json --output examples/benchmark/scale.json
```

## What It Tests

1. Generates a synthetic corpus of small test repositories
2. Runs batch scan with `--jobs 1`
3. Runs batch scan with `--jobs 2`
4. Verifies output semantics are identical (same scores, same statuses)
5. Records runtime for both configurations
6. Checks that runtime with parallel jobs is not significantly slower

## Output

### Markdown

```markdown
# Scale Gate Report

| Metric | Value |
|--------|-------|
| Corpus size | 20 |
| Jobs 1 runtime | 12.3s |
| Jobs 2 runtime | 8.1s |
| Semantic match | yes |
| Pass | yes |
```

### JSON

```json
{
  "corpus_size": 20,
  "jobs_1_runtime": 12.3,
  "jobs_2_runtime": 8.1,
  "semantic_match": true,
  "pass": true
}
```

## Notes

- Scale gate is an engineering regression test, not an academic performance benchmark
- Synthetic corpus is a test fixture, not a real-world adoption case
- Default thresholds are intentionally lenient
- Scale gate does not judge paper quality or scientific correctness
