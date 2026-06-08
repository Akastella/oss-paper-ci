"""Contract loading, validation, and template generation.

The reproducibility contract is an *optional* YAML file
(``reproducibility.yml``) that describes how to reproduce a scientific
paper's computational results.  This module handles parsing, validation,
and template generation for that contract.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

from oss_paper_ci.contract_schema import (
    CISpec,
    DataSpec,
    EnvironmentSpec,
    ExperimentSpec,
    FigureSpec,
    PaperSpec,
    ReproducibilityContract,
    ResultSpec,
)
from oss_paper_ci.models import CheckResult, Severity, Status

# Candidate filenames searched by find_contract()
_CONTRACT_FILENAMES = (
    "reproducibility.yml",
    "reproducibility.yaml",
    ".reproducibility.yml",
    ".reproducibility.yaml",
)


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def find_contract(repo_path: str) -> str | None:
    """Search for a reproducibility contract in *repo_path*.

    Returns the absolute path if found, otherwise ``None``.
    """
    root = Path(repo_path)
    for name in _CONTRACT_FILENAMES:
        candidate = root / name
        if candidate.exists():
            return str(candidate)
    return None


def load_contract(path: str) -> ReproducibilityContract:
    """Parse a YAML contract file and return a ``ReproducibilityContract``.

    Raises:
        FileNotFoundError: If *path* does not exist.
        yaml.YAMLError: If the YAML is malformed.
    """
    p = Path(path)
    if not p.exists():
        raise FileNotFoundError(f"Contract file not found: {path}")

    with open(p, encoding="utf-8") as f:
        data: dict[str, Any] = yaml.safe_load(f) or {}

    return _dict_to_contract(data)


def validate_contract(
    contract: ReproducibilityContract,
    repo_path: str,
) -> list[CheckResult]:
    """Validate that paths referenced in *contract* exist in *repo_path*.

    Returns a list of ``CheckResult`` objects.  An empty list means no
    issues were found.  Results use severity INFO for informational
    messages and WARNING/ERROR for actual problems.
    """
    root = Path(repo_path)
    results: list[CheckResult] = []

    # --- Paper ---
    if contract.paper.path:
        if not (root / contract.paper.path).exists():
            results.append(_warn(
                "CONTRACT",
                "Contract validation",
                f"Paper path does not exist: {contract.paper.path}",
            ))
        for bib in contract.paper.bibliography:
            if not (root / bib).exists():
                results.append(_warn(
                    "CONTRACT",
                    "Contract validation",
                    f"Bibliography file does not exist: {bib}",
                ))

    # --- Environment ---
    if contract.environment.file:
        if not (root / contract.environment.file).exists():
            results.append(_warn(
                "CONTRACT",
                "Contract validation",
                f"Environment file does not exist: {contract.environment.file}",
            ))

    # --- Data ---
    for ds in contract.data:
        if ds.availability in ("external", "not-required"):
            # External data is expected to be absent from the repo.
            continue
        if ds.path and not (root / ds.path).exists():
            results.append(_warn(
                "CONTRACT",
                "Contract validation",
                f"Data path does not exist: {ds.path} (id={ds.id})",
            ))

    # --- Experiments ---
    for exp in contract.experiments:
        if not exp.command:
            results.append(_warn(
                "CONTRACT",
                "Contract validation",
                f"Experiment has no command: {exp.id}",
            ))
            continue
        # Check if the command references a script file that should exist.
        _check_command_scripts(root, exp.command, exp.id, results)

    # --- Figures ---
    for fig in contract.figures:
        # Figures are *outputs* so they won't exist before running;
        # only warn if the directory doesn't exist.
        if fig.path:
            fig_dir = (root / fig.path).parent
            if not fig_dir.exists():
                results.append(_info(
                    "CONTRACT",
                    "Contract validation",
                    f"Figure output directory does not exist yet: {fig_dir}",
                ))

    # --- Results ---
    for res in contract.results:
        if res.path:
            res_dir = (root / res.path).parent
            if not res_dir.exists():
                results.append(_info(
                    "CONTRACT",
                    "Contract validation",
                    f"Result output directory does not exist yet: {res_dir}",
                ))

    return results


def generate_contract_template(template: str = "ml") -> str:
    """Generate a YAML contract template string.

    Args:
        template: One of ``"ml"``, ``"simulation"``, ``"data-science"``,
                  or ``"default"``.

    Returns:
        A YAML string suitable for writing to ``reproducibility.yml``.
    """
    if template == "ml":
        return _ML_TEMPLATE
    if template == "simulation":
        return _SIMULATION_TEMPLATE
    if template == "data-science":
        return _DATA_SCIENCE_TEMPLATE
    return _DEFAULT_TEMPLATE


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------


def _dict_to_contract(data: dict[str, Any]) -> ReproducibilityContract:
    """Convert a raw YAML dict into a ``ReproducibilityContract``."""
    paper_data = data.get("paper", {})
    env_data = data.get("environment", {})

    contract = ReproducibilityContract(
        version=str(data.get("version", "0.3")),
        project_name=data.get("project_name", ""),
        project_type=data.get("project_type", "other"),
        paper=PaperSpec(
            path=paper_data.get("path", ""),
            bibliography=paper_data.get("bibliography", []),
        ),
        environment=EnvironmentSpec(
            type=env_data.get("type", "python"),
            file=env_data.get("file", ""),
            python=env_data.get("python", ""),
            containers=env_data.get("containers", []),
        ),
    )

    # Data
    for item in data.get("data", []):
        contract.data.append(DataSpec(
            id=item.get("id", ""),
            path=item.get("path", ""),
            availability=item.get("availability", "external"),
            source=item.get("source", ""),
            license=item.get("license", ""),
            preprocessing=item.get("preprocessing", {}),
        ))

    # Experiments
    for item in data.get("experiments", []):
        contract.experiments.append(ExperimentSpec(
            id=item.get("id", ""),
            description=item.get("description", ""),
            command=item.get("command", ""),
            timeout_seconds=item.get("timeout_seconds", 60),
            safe_to_run=item.get("safe_to_run", False),
            expected_outputs=item.get("expected_outputs", []),
        ))

    # Figures
    for item in data.get("figures", []):
        contract.figures.append(FigureSpec(
            id=item.get("id", ""),
            path=item.get("path", ""),
            generated_by=item.get("generated_by", []),
            referenced_by=item.get("referenced_by", []),
        ))

    # Results
    for item in data.get("results", []):
        contract.results.append(ResultSpec(
            id=item.get("id", ""),
            path=item.get("path", ""),
            generated_by=item.get("generated_by", []),
        ))

    # CI
    ci_data = data.get("ci", {})
    if ci_data:
        contract.ci = CISpec(
            smoke_experiment=ci_data.get("smoke_experiment", ""),
            min_score=ci_data.get("min_score", 0),
            fail_on_regression=ci_data.get("fail_on_regression", False),
        )

    return contract


def _check_command_scripts(
    root: Path,
    command: str,
    exp_id: str,
    results: list[CheckResult],
) -> None:
    """If *command* references a script file, check it exists."""
    import re

    # Match common patterns: python script.py, sh script.sh, ./script
    patterns = [
        r"python3?\s+(\S+\.py)",
        r"(?:ba)?sh\s+(\S+\.sh)",
        r"\./(\S+)",
    ]
    for pat in patterns:
        for match in re.finditer(pat, command):
            script = match.group(1).lstrip("./")
            if not (root / script).exists():
                results.append(_warn(
                    "CONTRACT",
                    "Contract validation",
                    f"Script referenced by experiment '{exp_id}' does not exist: {script}",
                ))


def _warn(check_id: str, title: str, message: str) -> CheckResult:
    return CheckResult(
        id=check_id,
        title=title,
        severity=Severity.WARNING,
        status=Status.WARN,
        message=message,
    )


def _info(check_id: str, title: str, message: str) -> CheckResult:
    return CheckResult(
        id=check_id,
        title=title,
        severity=Severity.INFO,
        status=Status.WARN,
        message=message,
    )


# ---------------------------------------------------------------------------
# Templates
# ---------------------------------------------------------------------------

_DEFAULT_TEMPLATE = """\
# Reproducibility Contract for oss-paper-ci
# See: https://github.com/<owner>/<repo>
# Fill in the fields below to describe how to reproduce your paper.

version: "0.3"

project_name: "my-paper"
project_type: "other"  # ml | simulation | data-science | analysis | other

paper:
  path: "paper/main.pdf"
  bibliography:
    - "paper/references.bib"

environment:
  type: "python"       # python | conda | docker | r | julia | other
  file: "requirements.txt"
  python: "3.11"

data: []
#  - id: "dataset1"
#    path: "data/input.csv"
#    availability: "public"  # public | private | synthetic | external | not-required
#    source: "https://example.com/data.csv"
#    license: "CC-BY-4.0"

experiments: []
#  - id: "train"
#    description: "Train the model"
#    command: "python scripts/train.py"
#    timeout_seconds: 3600
#    safe_to_run: true
#    expected_outputs:
#      - "results/model.pkl"

figures: []
#  - id: "fig1"
#    path: "figures/loss_curve.png"
#    generated_by: ["train"]

results: []
#  - id: "accuracy"
#    path: "results/accuracy.json"
#    generated_by: ["train"]

ci:
  smoke_experiment: ""
  min_score: 0
  fail_on_regression: false
"""

_ML_TEMPLATE = """\
# Reproducibility Contract — Machine Learning Project
# Fill in the fields below to describe how to reproduce your paper.

version: "0.3"

project_name: "ml-paper"
project_type: "ml"

paper:
  path: "paper/main.tex"
  bibliography:
    - "paper/references.bib"

environment:
  type: "python"
  file: "requirements.txt"
  python: "3.11"

data:
  - id: "train-data"
    path: "data/train.csv"
    availability: "public"
    source: "https://example.com/train.csv"
    license: "CC-BY-4.0"
  - id: "test-data"
    path: "data/test.csv"
    availability: "public"
    source: "https://example.com/test.csv"
    license: "CC-BY-4.0"

experiments:
  - id: "train"
    description: "Train the model"
    command: "python scripts/train.py"
    timeout_seconds: 3600
    safe_to_run: true
    expected_outputs:
      - "results/model.pkl"
      - "results/metrics.json"
  - id: "evaluate"
    description: "Evaluate on test set"
    command: "python scripts/evaluate.py"
    timeout_seconds: 600
    safe_to_run: true
    expected_outputs:
      - "results/test_metrics.json"

figures:
  - id: "loss-curve"
    path: "figures/loss_curve.png"
    generated_by: ["train"]
    referenced_by: ["Section 4"]
  - id: "confusion-matrix"
    path: "figures/confusion_matrix.png"
    generated_by: ["evaluate"]
    referenced_by: ["Section 5"]

results:
  - id: "accuracy"
    path: "results/accuracy.json"
    generated_by: ["evaluate"]

ci:
  smoke_experiment: "train"
  min_score: 70
  fail_on_regression: true
"""

_SIMULATION_TEMPLATE = """\
# Reproducibility Contract — Simulation Project
# Fill in the fields below to describe how to reproduce your paper.

version: "0.3"

project_name: "simulation-paper"
project_type: "simulation"

paper:
  path: "paper/main.tex"
  bibliography:
    - "paper/references.bib"

environment:
  type: "conda"
  file: "environment.yml"
  python: "3.11"

data:
  - id: "initial-conditions"
    path: "data/initial_conditions.h5"
    availability: "public"
    source: "https://example.com/ics.h5"

experiments:
  - id: "run-simulation"
    description: "Run the main simulation"
    command: "python scripts/simulate.py"
    timeout_seconds: 7200
    safe_to_run: true
    expected_outputs:
      - "results/output.h5"

figures:
  - id: "field-plot"
    path: "figures/field_snapshot.png"
    generated_by: ["run-simulation"]

results:
  - id: "convergence"
    path: "results/convergence.csv"
    generated_by: ["run-simulation"]

ci:
  smoke_experiment: "run-simulation"
  min_score: 70
  fail_on_regression: false
"""

_DATA_SCIENCE_TEMPLATE = """\
# Reproducibility Contract — Data Science / Analysis Project
# Fill in the fields below to describe how to reproduce your paper.

version: "0.3"

project_name: "data-science-paper"
project_type: "data-science"

paper:
  path: "paper/main.pdf"
  bibliography:
    - "paper/references.bib"

environment:
  type: "python"
  file: "requirements.txt"
  python: "3.11"

data:
  - id: "raw-data"
    path: "data/raw/"
    availability: "public"
    source: "https://example.com/dataset.zip"
    license: "CC0-1.0"
    preprocessing:
      script: "scripts/preprocess.py"
      outputs:
        - "data/clean.csv"

experiments:
  - id: "analysis"
    description: "Run the full analysis pipeline"
    command: "python scripts/analyze.py"
    timeout_seconds: 1200
    safe_to_run: true
    expected_outputs:
      - "results/summary.csv"

figures:
  - id: "main-plot"
    path: "figures/main_figure.png"
    generated_by: ["analysis"]
    referenced_by: ["Figure 1"]

results:
  - id: "summary-stats"
    path: "results/summary.csv"
    generated_by: ["analysis"]

ci:
  smoke_experiment: "analysis"
  min_score: 60
  fail_on_regression: false
"""
