"""Python language adapter."""
from __future__ import annotations
from pathlib import Path
from typing import Any
from .base import AdapterBase, AdapterDetection, AdapterPlan, ArtifactRule, MetricRule, SafetyRule, Step

class PythonAdapter(AdapterBase):
    @property
    def name(self): return "python"
    @property
    def display_name(self): return "Python"
    @property
    def aliases(self): return ["python3", "py"]
    @property
    def ecosystem(self): return "scripting"
    @property
    def supports_execute(self): return True
    @property
    def requires_runtime(self): return ["python3", "python"]
    def detect(self, path):
        env_files = self._find_files(path, ["pyproject.toml", "requirements.txt", "requirements*.txt", "setup.py", "setup.cfg", "environment.yml", "conda.yml", "Pipfile", "uv.lock", "poetry.lock"])
        entrypoints = self._find_files(path, ["main.py", "run.py", "train.py", "evaluate.py", "analyze.py", "reproduce.py", "scripts/*.py", "src/*.py"])
        notebooks = self._find_files(path, ["*.ipynb", "notebooks/*.ipynb"])
        evidence = env_files + notebooks
        if not evidence and not entrypoints: return None
        all_evidence = sorted(set(evidence + entrypoints[:5]))
        confidence = self._confidence_from_evidence(env_files, entrypoints)
        runtime = self._check_runtime_available("python3")
        if not runtime.available: runtime = self._check_runtime_available("python")
        return AdapterDetection(name=self.name, display_name=self.display_name, confidence=confidence, evidence=all_evidence, runtime=runtime, supports_dry_run=True, supports_execute=True)
    def plan(self, path):
        install_steps, run_steps, warnings, notes = [], [], [], []
        env_files = self._find_files(path, ["uv.lock", "poetry.lock", "requirements.txt", "requirements*.txt", "pyproject.toml", "setup.py", "setup.cfg", "environment.yml", "conda.yml", "Pipfile"])
        if any("uv.lock" in f for f in env_files):
            install_steps.append(Step(command="uv sync", description="Install dependencies with uv", requires_network=True))
        elif any("poetry.lock" in f for f in env_files):
            install_steps.append(Step(command="poetry install", description="Install dependencies with poetry", requires_network=True))
        elif any("environment.yml" in f or "conda.yml" in f for f in env_files):
            env_file = next(f for f in env_files if "environment.yml" in f or "conda.yml" in f)
            install_steps.append(Step(command=f"conda env create -f {env_file}", description="Create conda environment", requires_network=True))
        elif any("requirements.txt" in f for f in env_files):
            req_file = next(f for f in env_files if "requirements.txt" in f)
            install_steps.append(Step(command=f"python -m pip install -r {req_file}", description="Install pip dependencies", requires_network=True))
        elif any("pyproject.toml" in f for f in env_files):
            install_steps.append(Step(command="python -m pip install -e .", description="Install project in editable mode", requires_network=True))
        entrypoints = self._find_files(path, ["scripts/*.py", "main.py", "run.py", "train.py", "evaluate.py", "reproduce.py"])
        for ep in entrypoints[:5]:
            run_steps.append(Step(command=f"python {ep}", description=f"Run {ep}"))
        if not run_steps: warnings.append("No Python entrypoints found")
        return AdapterPlan(adapter_name=self.name, install_steps=install_steps, run_steps=run_steps, steps=install_steps + run_steps, warnings=warnings, notes=notes)
    def artifact_rules(self, path):
        return [ArtifactRule(pattern="results/**", description="Results directory"), ArtifactRule(pattern="figures/**", description="Figures", artifact_type="figure"), ArtifactRule(pattern="metrics.json", description="Metrics file")]
    def metric_rules(self, path):
        return [MetricRule(pattern="metrics.json", format="json", description="Main metrics")]
    def safety_rules(self, path):
        return [SafetyRule(rule_type="block_command", pattern="rm -rf /", message="Recursive delete blocked", severity="error")]
    def report_hints(self, path):
        return {"language": "python", "package_managers": ["pip", "conda", "poetry", "uv"]}
