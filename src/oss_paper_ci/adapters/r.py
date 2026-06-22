"""R language adapter."""
from __future__ import annotations
from pathlib import Path
from .base import AdapterBase, AdapterDetection, AdapterPlan, ArtifactRule, MetricRule, SafetyRule, Step

class RAdapter(AdapterBase):
    @property
    def name(self): return "r"
    @property
    def display_name(self): return "R"
    @property
    def aliases(self): return ["rscript", "r-lang"]
    @property
    def ecosystem(self): return "scripting"
    @property
    def supports_execute(self): return True
    @property
    def requires_runtime(self): return ["Rscript"]
    def detect(self, path):
        env_files = self._find_files(path, ["DESCRIPTION", "renv.lock", "install.R", ".Rprofile", "NAMESPACE"])
        entrypoints = self._find_files(path, ["scripts/*.R", "scripts/*.r", "analysis/*.R", "*.R", "run.R", "main.R", "reproduce.R"])
        notebooks = self._find_files(path, ["*.Rmd", "*.rmd", "*.qmd"])
        evidence = env_files + notebooks
        if not evidence and not entrypoints: return None
        all_evidence = sorted(set(evidence + entrypoints[:5]))
        confidence = self._confidence_from_evidence(env_files, entrypoints)
        runtime = self._check_runtime_available("Rscript")
        limitations = []
        if not runtime.available: limitations.append("R runtime (Rscript) must be installed separately.")
        limitations.append("renv restoration requires renv package.")
        return AdapterDetection(name=self.name, display_name=self.display_name, confidence=confidence, evidence=all_evidence, runtime=runtime, supports_dry_run=True, supports_execute=runtime.available, limitations=limitations)
    def plan(self, path):
        install_steps, run_steps, warnings, notes = [], [], [], []
        if self._find_files(path, ["renv.lock"]):
            install_steps.append(Step(command="Rscript -e 'renv::restore()'", description="Restore R packages with renv", requires_network=True))
        elif self._find_files(path, ["install.R"]):
            install_steps.append(Step(command="Rscript install.R", description="Run install.R", requires_network=True))
        elif self._find_files(path, ["DESCRIPTION"]):
            install_steps.append(Step(command="Rscript -e 'devtools::install_deps()'", description="Install package dependencies", requires_network=True))
        entrypoints = self._find_files(path, ["scripts/*.R", "scripts/*.r", "run.R", "main.R", "reproduce.R"])
        for ep in entrypoints[:5]:
            run_steps.append(Step(command=f"Rscript {ep}", description=f"Run {ep}"))
        rmds = self._find_files(path, ["*.Rmd", "*.rmd", "analysis/*.Rmd"])
        for rmd in rmds[:3]:
            run_steps.append(Step(command=f"Rscript -e 'rmarkdown::render(\"{rmd}\")'", description=f"Render {rmd}"))
        if not run_steps: warnings.append("No R entrypoints found")
        return AdapterPlan(adapter_name=self.name, install_steps=install_steps, run_steps=run_steps, steps=install_steps + run_steps, warnings=warnings, notes=notes)
    def artifact_rules(self, path):
        return [ArtifactRule(pattern="output/**", description="Output directory"), ArtifactRule(pattern="figures/**", description="Figures", artifact_type="figure")]
    def safety_rules(self, path):
        return [SafetyRule(rule_type="warn", pattern="install.packages", message="install.packages() may modify the R library", severity="warning")]
