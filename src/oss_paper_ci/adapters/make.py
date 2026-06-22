"""Make workflow adapter."""
from __future__ import annotations
from pathlib import Path
from .base import AdapterBase, AdapterDetection, AdapterPlan, ArtifactRule, SafetyRule, Step

class MakeAdapter(AdapterBase):
    @property
    def name(self): return "make"
    @property
    def display_name(self): return "Make"
    @property
    def aliases(self): return ["makefile", "gnu-make"]
    @property
    def ecosystem(self): return "workflow"
    @property
    def supports_execute(self): return True
    @property
    def requires_runtime(self): return ["make"]
    def detect(self, path):
        makefiles = self._find_files(path, ["Makefile", "makefile", "GNUmakefile"])
        if not makefiles: return None
        confidence = 0.9 if "Makefile" in makefiles else 0.7
        runtime = self._check_runtime_available("make")
        return AdapterDetection(name=self.name, display_name=self.display_name, confidence=confidence, evidence=makefiles, runtime=runtime, supports_dry_run=True, supports_execute=runtime.available)
    def plan(self, path):
        steps, warnings, notes = [], [], []
        targets = self._parse_makefile_targets(path)
        preferred = ["reproduce", "all", "test", "figures", "tables", "paper"]
        found_targets = [t for t in preferred if t in targets]
        if found_targets:
            primary = found_targets[0]
            steps.append(Step(command=f"make {primary}", description=f"Run make target: {primary}"))
            notes.append(f"Primary target: {primary}")
            if len(found_targets) > 1:
                notes.append(f"Other targets: {', '.join(found_targets[1:])}")
        elif targets:
            steps.append(Step(command="make", description="Run default make target"))
            notes.append(f"Available targets: {', '.join(sorted(targets)[:10])}")
        else:
            warnings.append("No Make targets found")
        return AdapterPlan(adapter_name=self.name, steps=steps, install_steps=[], run_steps=steps, warnings=warnings, notes=notes)
    def _parse_makefile_targets(self, path):
        targets = []
        for name in ["Makefile", "makefile", "GNUmakefile"]:
            p = path / name
            if p.exists():
                try:
                    for line in p.read_text(encoding="utf-8", errors="ignore").split("\n"):
                        line = line.strip()
                        if line and not line.startswith("#") and ":" in line:
                            target = line.split(":")[0].strip()
                            if target and not target.startswith(".") and " " not in target:
                                targets.append(target)
                except Exception: pass
                break
        return targets
    def artifact_rules(self, path):
        return [ArtifactRule(pattern="output/**", description="Output"), ArtifactRule(pattern="figures/**", description="Figures", artifact_type="figure"), ArtifactRule(pattern="tables/**", description="Tables", artifact_type="table")]
    def safety_rules(self, path):
        return [SafetyRule(rule_type="warn", pattern="make clean", message="make clean may delete output", severity="warning")]
