"""MATLAB/Octave language adapter."""
from __future__ import annotations
from pathlib import Path
from .base import AdapterBase, AdapterDetection, AdapterPlan, ArtifactRule, SafetyRule, Step

class MatlabAdapter(AdapterBase):
    @property
    def name(self): return "matlab"
    @property
    def display_name(self): return "MATLAB/Octave"
    @property
    def aliases(self): return ["octave", "matlab-octave"]
    @property
    def ecosystem(self): return "numerical"
    @property
    def supports_execute(self): return False
    @property
    def requires_runtime(self): return ["matlab", "octave"]
    def detect(self, path):
        m_files = self._find_files(path, ["*.m", "scripts/*.m", "src/*.m"])
        entrypoints = self._find_files(path, ["startup.m", "run.m", "run_*.m", "main.m", "reproduce.m"])
        if not m_files and not entrypoints: return None
        all_evidence = sorted(set(m_files[:10] + entrypoints))
        confidence = self._confidence_from_evidence(entrypoints, m_files)
        matlab_runtime = self._check_runtime_available("matlab")
        octave_runtime = self._check_runtime_available("octave")
        runtime = matlab_runtime if matlab_runtime.available else octave_runtime
        return AdapterDetection(name=self.name, display_name=self.display_name, confidence=confidence, evidence=all_evidence, runtime=runtime, supports_dry_run=True, supports_execute=octave_runtime.available, limitations=["MATLAB requires a commercial license.", "Octave can be used as a fallback."])
    def plan(self, path):
        steps, warnings, notes = [], [], ["MATLAB execution requires a license or Octave fallback."]
        entrypoints = self._find_files(path, ["run*.m", "main.m", "startup.m", "reproduce.m"])
        if entrypoints:
            ep = entrypoints[0]
            steps.append(Step(command=f"octave --no-gui --eval \"run('{ep}')\"", description=f"Run {ep} with Octave"))
        else:
            warnings.append("No MATLAB/Octave entrypoints found")
        return AdapterPlan(adapter_name=self.name, steps=steps, install_steps=[], run_steps=steps, warnings=warnings, notes=notes)
    def artifact_rules(self, path):
        return [ArtifactRule(pattern="output/**", description="Output"), ArtifactRule(pattern="*.fig", description="MATLAB figures"), ArtifactRule(pattern="*.mat", description="MATLAB data")]
    def safety_rules(self, path):
        return [SafetyRule(rule_type="warn", pattern="system(", message="MATLAB system() calls execute shell commands", severity="warning")]
