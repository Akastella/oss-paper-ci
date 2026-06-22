"""Snakemake workflow adapter."""
from __future__ import annotations
from pathlib import Path
from .base import AdapterBase, AdapterDetection, AdapterPlan, ArtifactRule, SafetyRule, Step

class SnakemakeAdapter(AdapterBase):
    @property
    def name(self): return "snakemake"
    @property
    def display_name(self): return "Snakemake"
    @property
    def aliases(self): return ["smk", "snake"]
    @property
    def ecosystem(self): return "workflow"
    @property
    def supports_execute(self): return False
    @property
    def requires_runtime(self): return ["snakemake"]
    def detect(self, path):
        snakefiles = self._find_files(path, ["Snakefile", "workflow/Snakefile", "*.smk", "workflow/rules/*.smk"])
        if not snakefiles: return None
        config_files = self._find_files(path, ["config.yaml", "config.yml", "workflow/config.yaml"])
        all_evidence = sorted(set(snakefiles + config_files))
        confidence = self._confidence_from_evidence(snakefiles, config_files)
        runtime = self._check_runtime_available("snakemake")
        limitations = ["Snakemake runtime must be installed separately.", "Workflow execution may require significant resources."]
        return AdapterDetection(name=self.name, display_name=self.display_name, confidence=confidence, evidence=all_evidence, runtime=runtime, supports_dry_run=True, supports_execute=False, limitations=limitations)
    def plan(self, path):
        steps, warnings, notes = [], [], ["Snakemake workflows are dry-run only by default."]
        steps.append(Step(command="snakemake -n", description="Dry-run: show planned jobs"))
        return AdapterPlan(adapter_name=self.name, steps=steps, install_steps=[], run_steps=steps, warnings=warnings, notes=notes)
    def artifact_rules(self, path):
        return [ArtifactRule(pattern="results/**", description="Results"), ArtifactRule(pattern="output/**", description="Output")]
    def safety_rules(self, path):
        return [SafetyRule(rule_type="require_flag", pattern="snakemake --cores", message="Execution requires --cores flag", severity="error")]
