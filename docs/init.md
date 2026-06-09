# Init Command

The `init` command scaffolds reproducibility assets for your repository.

## Usage

```bash
oss-paper-ci init --contract          # Generate reproducibility.yml
oss-paper-ci init --workflow          # Generate GitHub Actions workflow
oss-paper-ci init --all               # Generate both
oss-paper-ci init --dry-run           # Show what would be created
oss-paper-ci init --force             # Overwrite existing files
```

## What it generates

### reproducibility.yml

A template contract defining experiment steps:

```yaml
experiments:
  - id: train
    command: python scripts/train.py
    timeout: 300
  - id: evaluate
    command: python scripts/evaluate.py
    depends_on: [train]
```

Edit this file to match your actual experiment structure.

### GitHub Actions workflow

A `.github/workflows/oss-paper-ci.yml` that runs reproducibility checks on
push and pull request events.

## Options

| Option | Description |
|--------|-------------|
| `--contract` | Generate reproducibility.yml |
| `--workflow` | Generate .github/workflows/oss-paper-ci.yml |
| `--all` | Generate both contract and workflow |
| `--dry-run` | Show files without creating them |
| `--force` | Overwrite existing files |
| `--template` | Contract template: ml, simulation, data-science, default |

## Limitations

- Init generates generic templates; you must customize them
- Init does not detect your experiment structure automatically
- Init does not commit files to git

## After init

1. Edit `reproducibility.yml` to match your experiments
2. Review the generated workflow
3. Run `oss-paper-ci scan .` to check your repository
