# Demo Paper Repository

`examples/demo-paper-repo/` is a toy-but-realistic scientific paper repository
for demonstrating oss-paper-ci.

## Structure

```
demo-paper-repo/
  README.md
  LICENSE
  requirements.txt
  environment.yml
  reproducibility.yml
  scripts/
    train.py
    evaluate.py
    make_figures.py
  data/
    README.md
  results/
    README.md
    metrics.json
  figures/
    README.md
```

## Purpose

This repository is included to:
- Show what a well-structured paper repository looks like
- Provide a testable example for oss-paper-ci
- Demonstrate output formats with a realistic project

**Important:** This is a synthetic demo, not a real research project. No
adoption claims are made.

## Try it

```bash
oss-paper-ci scan examples/demo-paper-repo --format markdown
oss-paper-ci doctor examples/demo-paper-repo
oss-paper-ci graph examples/demo-paper-repo --format markdown
```

## Replace with your project

To use oss-paper-ci on your own repository:

1. Copy the structure (scripts/, data/, results/, figures/)
2. Create your own requirements.txt or pyproject.toml
3. Edit reproducibility.yml to match your experiments
4. Run `oss-paper-ci scan .`
