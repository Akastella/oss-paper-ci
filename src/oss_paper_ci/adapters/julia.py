"""Julia language adapter."""
from __future__ import annotations
from pathlib import Path
from .base import AdapterBase, AdapterDetection, AdapterPlan, ArtifactRule, SafetyRule, Step

class JuliaAdapter(AdapterBase):
    @property
    def name(self): return "julia"
    @property
    def display_name(self): return "Julia"
    @property
    def aliases(self): return ["jl"]
    @property
    def ecosystem(self): return "scripting"
    @property
    def supports_execute(self): return True
    @property
    def requires_runtime(self): return ["julia"]
    def detect(self, path):
        env_files = self._find_files(path, ["Project.toml", "Manifest.toml"])
        entrypoints = self._find_files(path, ["scripts/*.jl", "*.jl", "main.jl", "run.jl", "reproduce.jl"])
        if not env_files and not entrypoints: return None
        all_evidence = sorted(set(env_files + entrypoints[:5]))
        confidence = self._confidence_from_evidence(env_files, entrypoints)
        runtime = self._check_runtime_available("julia")
        limitations = []
        if not runtime.available: limitations.append("Julia runtime must be installed separately.")
        return AdapterDetection(name=self.name, display_name=self.display_name, confidence=confidence, evidence=all_evidence, runtime=runtime, supports_dry_run=True, supports_execute=runtime.available, limitations=limitations)
    def plan(self, path):
        install_steps, run_steps, warnings, notes = [], [], [], []
        if self._find_files(path, ["Project.toml"]):
            install_steps.append(Step(command="julia --project -e 'using Pkg; Pkg.instantiate()'", description="Instantiate Julia project", requires_network=True))
        entrypoints = self._find_files(path, ["scripts/*.jl", "main.jl", "run.jl", "reproduce.jl"])
        for ep in entrypoints[:5]:
            run_steps.append(Step(command=f"julia --project {ep}", description=f"Run {ep}"))
        if not run_steps: warnings.append("No Julia entrypoints found")
        return AdapterPlan(adapter_name=self.name, install_steps=install_steps, run_steps=run_steps, steps=install_steps + run_steps, warnings=warnings, notes=notes)
    def artifact_rules(self, path):
        return [ArtifactRule(pattern="output/**", description="Output directory")]
    def safety_rules(self, path):
        return [SafetyRule(rule_type="warn", pattern="Pkg.add", message="Pkg.add() may modify the project", severity="warning")]
