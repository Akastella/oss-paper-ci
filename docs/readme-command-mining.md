# README Command Mining

README command mining extracts install, train, evaluate, test, figure, and data commands from documentation files.

## How It Works

### Fenced Code Blocks

Commands are extracted from fenced code blocks with language hints:

````markdown
```bash
python scripts/train.py --epochs 10
```
````

Supported language hints: `bash`, `sh`, `shell`, `zsh`, `console`, `terminal`, or no hint.

### Inline Commands

Commands wrapped in backticks are also extracted:

```markdown
Run `python scripts/train.py` to train the model.
```

### Section Context

Commands are classified based on the surrounding section heading:

- Section "## Installation" → `install` kind
- Section "## Training" → `train` kind
- Section "## Evaluation" → `evaluate` kind

## Command Classification

Commands are classified into kinds:

| Kind | Description | Examples |
|------|-------------|----------|
| `install` | Dependency installation | `pip install -r requirements.txt` |
| `train` | Model training | `python scripts/train.py` |
| `evaluate` | Model evaluation | `python scripts/evaluate.py` |
| `test` | Testing | `pytest tests/` |
| `figure` | Figure generation | `python scripts/plot.py` |
| `data` | Data processing | `python scripts/preprocess.py` |
| `unknown` | Unclassified | Other commands |

## Confidence

Each command candidate has a confidence score:
- Fenced code blocks: 0.7
- Inline commands: 0.5

## Dangerous Commands

Commands matching dangerous patterns are flagged:
- `sudo`, `rm -rf /`, `curl | sh`, `wget | bash`
- `git push`, `npm publish`, `twine upload`
- `shutdown`, `reboot`, `kill -9 1`

Flagged commands are included in the intake report but excluded from autoplan candidates.

## Limitations

- Only markdown and text files are scanned
- Multi-line commands (with `\`) are joined
- Commands with `$` or `>` prefixes are cleaned
- Very long commands are truncated in reports
