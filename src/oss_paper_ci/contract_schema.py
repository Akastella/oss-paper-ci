"""Dataclass schema for the Reproducibility Contract.

Each dataclass maps to a section of the ``reproducibility.yml`` file.
All fields have sensible defaults so that a contract can be partially
filled in and still parse without errors.
"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class PaperSpec:
    """Location of the paper manuscript and bibliography."""

    path: str = ""
    bibliography: list[str] = field(default_factory=list)


@dataclass
class EnvironmentSpec:
    """How to recreate the computational environment."""

    type: str = "python"  # python | conda | docker | r | julia | other
    file: str = ""  # path to requirements.txt, environment.yml, Dockerfile, etc.
    python: str = ""  # e.g. "3.11"
    containers: list[dict] = field(default_factory=list)


@dataclass
class DataSpec:
    """Description of one dataset used by the project."""

    id: str = ""
    path: str = ""
    availability: str = (
        "external"  # public | private | synthetic | external | not-required
    )
    source: str = ""  # URL or citation for downloading
    license: str = ""
    preprocessing: dict = field(default_factory=dict)


@dataclass
class ExperimentSpec:
    """A single reproducible experiment (training run, simulation, etc.)."""

    id: str = ""
    description: str = ""
    command: str = ""  # shell command to run
    timeout_seconds: int = 60
    safe_to_run: bool = False  # True = may be run in CI
    expected_outputs: list[str] = field(default_factory=list)


@dataclass
class FigureSpec:
    """A figure produced by experiments and referenced in the paper."""

    id: str = ""
    path: str = ""  # output path of the figure file
    generated_by: list[str] = field(default_factory=list)  # experiment IDs
    referenced_by: list[str] = field(default_factory=list)  # paper sections


@dataclass
class ResultSpec:
    """A numerical result or table produced by experiments."""

    id: str = ""
    path: str = ""
    generated_by: list[str] = field(default_factory=list)  # experiment IDs


@dataclass
class CISpec:
    """CI/CD integration settings."""

    smoke_experiment: str = ""  # experiment ID to run as smoke test
    min_score: int = 0  # minimum reproducibility score to pass
    fail_on_regression: bool = False  # fail if score drops


@dataclass
class ReproducibilityContract:
    """Top-level contract schema, mapping to ``reproducibility.yml``."""

    version: str = "0.3"
    project_name: str = ""
    project_type: str = "other"  # ml | simulation | data-science | analysis | other
    paper: PaperSpec = field(default_factory=PaperSpec)
    environment: EnvironmentSpec = field(default_factory=EnvironmentSpec)
    data: list[DataSpec] = field(default_factory=list)
    experiments: list[ExperimentSpec] = field(default_factory=list)
    figures: list[FigureSpec] = field(default_factory=list)
    results: list[ResultSpec] = field(default_factory=list)
    ci: CISpec = field(default_factory=CISpec)
