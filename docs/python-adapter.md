# Python Adapter

The Python adapter detects Python projects and generates reproduction plans.

## Detection

Files detected:
- `pyproject.toml`, `requirements.txt`, `setup.py`, `setup.cfg`
- `environment.yml`, `conda.yml`, `Pipfile`, `poetry.lock`, `uv.lock`
- `*.ipynb` notebooks
- `main.py`, `run.py`, `train.py`, `evaluate.py`, `scripts/*.py`

## Planning

Install steps are generated based on detected environment files:
- `uv.lock` → `uv sync`
- `poetry.lock` → `poetry install`
- `environment.yml` → `conda env create`
- `requirements.txt` → `pip install -r requirements.txt`
- `pyproject.toml` → `pip install -e .`

## Runtime

Requires: `python3` or `python`

Python is the primary supported language (support level: **native**).

## Safety

- Commands are checked for dangerous patterns before execution
- Default to dry-run; `--execute` required for actual execution

## Limitations

- Conda environments are not fully automated
- Poetry projects may require manual setup
- Some packages may need system libraries
