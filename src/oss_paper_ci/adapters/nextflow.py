"""Nextflow workflow adapter."""
from __future__ import annotations
from pathlib import Path
from .base import AdapterBase, AdapterDetection, AdapterPlan, ArtifactRule, SafetyRule, Step

class NextflowAdapter(AdapterBase):
    @property
    def name(self): return "nextflow"
    @property
    def display_name(self): return "Nextflow"
    @property
    def aliases(self): return ["nf"]
    @property
    def ecosystem(self): return "workflow"
    @property
    def supports_execute(self): return False
    @property
    def requires_runtime(self): return ["nextflow"]
    def detect(self, path):
        env_files = self._find_files(path, ["main.nf", "nextflow.config", "modules/**/*.nf"])
        if not env_files: return None
        confidence = self._confidence_from_evidence(env_files, [])
        runtime = self._check_runtime_available("nextflow")
        limitations = ["Nextflow runtime must be installed separately.", "Workflow may require significant resources."]
        return AdapterDetection(name=self.name, display_name=self.display_name, confidence=confidence, evidence=env_files, runtime=runtime, supports_dry_run=True, supports_execute=False, limitations=limitations)
    def plan(self, path):
        steps, warnings, notes = [], [], ["Nextflow workflows are dry-run only by default."]
        steps.append(Step(command="nextflow run . -preview", description="Preview planned processes"))
        return AdapterPlan(adapter_name=self.name, steps=steps, install_steps=[], run_steps=steps, warnings=warnings, notes=notes)
    def artifact_rules(self, path):
        return [ArtifactRule(pattern="results/**", description="Results"), ArtifactRule(pattern="work/**", description="Work directory")]
    def safety_rules(self, path):
        return [SafetyRule(rule_type="require_flag", pattern="nextflow run", message="Execution requires explicit confirmation", severity="error")]
