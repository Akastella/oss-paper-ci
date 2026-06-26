"""Shell script adapter."""
from __future__ import annotations
import re
from pathlib import Path
from .base import AdapterBase, AdapterDetection, AdapterPlan, ArtifactRule, SafetyRule, Step

_DANGEROUS_PATTERNS = ["rm -rf /", "rm -rf ~", "rm -rf /*", "mkfs.", "dd if=", "> /dev/sd", "chmod -R 777 /", "curl | bash", "wget | bash", "curl | sh", "wget | sh", "eval $(curl", "eval $(wget"]

# Regex patterns for dangerous commands with arguments
_DANGEROUS_REGEX = [
    re.compile(r"curl\s+.*\|\s*(ba)?sh"),
    re.compile(r"wget\s+.*\|\s*(ba)?sh"),
    re.compile(r"eval\s+\$\(curl"),
    re.compile(r"eval\s+\$\(wget"),
]

class ShellAdapter(AdapterBase):
    @property
    def name(self): return "shell"
    @property
    def display_name(self): return "Shell Scripts"
    @property
    def aliases(self): return ["bash", "sh", "shellscript"]
    @property
    def ecosystem(self): return "workflow"
    @property
    def supports_execute(self): return True
    @property
    def requires_runtime(self): return ["bash"]
    def detect(self, path):
        entrypoints = self._find_files(path, ["run.sh", "reproduce.sh", "scripts/*.sh", "*.sh", "setup.sh"])
        if not entrypoints: return None
        confidence = 0.6
        for ep in entrypoints:
            if "reproduce" in ep.lower(): confidence = 0.85; break
            if "run" in ep.lower(): confidence = 0.75
        runtime = self._check_runtime_available("bash")
        return AdapterDetection(name=self.name, display_name=self.display_name, confidence=confidence, evidence=entrypoints, runtime=runtime, supports_dry_run=True, supports_execute=runtime.available, warnings=["Shell scripts may contain arbitrary commands. Review before execution."])
    def plan(self, path):
        steps, warnings, notes = [], [], ["Shell scripts execute arbitrary commands. Review before running."]
        entrypoints = self._find_files(path, ["reproduce.sh", "run.sh", "scripts/*.sh"])
        for ep in entrypoints[:3]:
            is_dangerous = self._check_script_dangerous(path / ep)
            steps.append(Step(command=f"bash {ep}", description=f"Run {ep}", is_dangerous=is_dangerous))
            if is_dangerous: warnings.append(f"{ep} contains potentially dangerous commands")
        if not steps: warnings.append("No shell entrypoints found")
        return AdapterPlan(adapter_name=self.name, steps=steps, install_steps=[], run_steps=steps, warnings=warnings, notes=notes)
    def _check_script_dangerous(self, script_path):
        try:
            content = script_path.read_text(encoding="utf-8", errors="ignore")
            for pattern in _DANGEROUS_PATTERNS:
                if pattern in content: return True
            for regex in _DANGEROUS_REGEX:
                if regex.search(content): return True
        except Exception: pass
        return False
    def safety_rules(self, path):
        return [
            SafetyRule(rule_type="block_command", pattern="rm -rf /", message="Recursive delete of root blocked", severity="error"),
            SafetyRule(rule_type="block_command", pattern="curl | bash", message="Piping curl to bash is blocked", severity="error"),
            SafetyRule(rule_type="block_command", pattern="wget | bash", message="Piping wget to bash is blocked", severity="error"),
            SafetyRule(rule_type="warn", pattern="sudo ", message="sudo requires elevated privileges", severity="warning"),
        ]
    def artifact_rules(self, path):
        return [ArtifactRule(pattern="output/**", description="Output"), ArtifactRule(pattern="results/**", description="Results")]
    def report_hints(self, path):
        return {"language": "shell", "safety_level": "high"}
