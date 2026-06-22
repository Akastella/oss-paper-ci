"""Base classes and data structures for language adapters."""
from __future__ import annotations
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

@dataclass
class Step:
    command: str
    description: str = ""
    working_dir: str = ""
    env_vars: dict[str, str] = field(default_factory=dict)
    timeout_seconds: int = 300
    is_dangerous: bool = False
    requires_network: bool = False
    requires_runtime: bool = True
    def to_dict(self) -> dict[str, Any]:
        d: dict[str, Any] = {"command": self.command}
        if self.description: d["description"] = self.description
        if self.is_dangerous: d["is_dangerous"] = True
        if self.requires_network: d["requires_network"] = True
        if not self.requires_runtime: d["requires_runtime"] = False
        return d

@dataclass
class RuntimeInfo:
    name: str
    available: bool = False
    version: str = ""
    path: str = ""
    error: str = ""
    def to_dict(self) -> dict[str, Any]:
        d: dict[str, Any] = {"name": self.name, "available": self.available}
        if self.version: d["version"] = self.version
        if self.path: d["path"] = self.path
        if self.error: d["error"] = self.error
        return d

@dataclass
class AdapterDetection:
    name: str
    display_name: str
    confidence: float
    evidence: list[str] = field(default_factory=list)
    runtime: RuntimeInfo | None = None
    supports_dry_run: bool = True
    supports_execute: bool = False
    limitations: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    def to_dict(self) -> dict[str, Any]:
        d: dict[str, Any] = {"name": self.name, "display_name": self.display_name, "confidence": round(self.confidence, 2), "evidence": sorted(self.evidence), "supports_dry_run": self.supports_dry_run, "supports_execute": self.supports_execute}
        if self.runtime: d["runtime"] = self.runtime.to_dict()
        if self.limitations: d["limitations"] = sorted(self.limitations)
        if self.warnings: d["warnings"] = sorted(self.warnings)
        return d

@dataclass
class AdapterPlan:
    adapter_name: str
    steps: list[Step] = field(default_factory=list)
    install_steps: list[Step] = field(default_factory=list)
    run_steps: list[Step] = field(default_factory=list)
    estimated_duration_seconds: int = 0
    warnings: list[str] = field(default_factory=list)
    notes: list[str] = field(default_factory=list)
    def to_dict(self) -> dict[str, Any]:
        d: dict[str, Any] = {"adapter_name": self.adapter_name, "steps": [s.to_dict() for s in self.steps], "install_steps": [s.to_dict() for s in self.install_steps], "run_steps": [s.to_dict() for s in self.run_steps]}
        if self.warnings: d["warnings"] = sorted(self.warnings)
        if self.notes: d["notes"] = sorted(self.notes)
        return d

@dataclass
class ArtifactRule:
    pattern: str
    description: str = ""
    required: bool = False
    artifact_type: str = "file"
    def to_dict(self) -> dict[str, Any]:
        d: dict[str, Any] = {"pattern": self.pattern}
        if self.description: d["description"] = self.description
        if self.required: d["required"] = True
        return d

@dataclass
class MetricRule:
    pattern: str
    format: str = "json"
    description: str = ""
    def to_dict(self) -> dict[str, Any]:
        d: dict[str, Any] = {"pattern": self.pattern, "format": self.format}
        if self.description: d["description"] = self.description
        return d

@dataclass
class SafetyRule:
    rule_type: str
    pattern: str
    message: str
    severity: str = "error"
    def to_dict(self) -> dict[str, Any]:
        return {"rule_type": self.rule_type, "pattern": self.pattern, "message": self.message, "severity": self.severity}

class AdapterBase(ABC):
    @property
    @abstractmethod
    def name(self) -> str: ...
    @property
    @abstractmethod
    def display_name(self) -> str: ...
    @property
    def aliases(self) -> list[str]: return []
    @property
    def ecosystem(self) -> str: return "general"
    @property
    def supports_execute(self) -> bool: return False
    @property
    def supports_dry_run(self) -> bool: return True
    @property
    def requires_runtime(self) -> list[str]: return []
    @abstractmethod
    def detect(self, path: Path) -> AdapterDetection | None: ...
    @abstractmethod
    def plan(self, path: Path) -> AdapterPlan: ...
    def artifact_rules(self, path: Path) -> list[ArtifactRule]: return []
    def metric_rules(self, path: Path) -> list[MetricRule]: return []
    def safety_rules(self, path: Path) -> list[SafetyRule]: return []
    def report_hints(self, path: Path) -> dict[str, Any]: return {}
    def _check_runtime_available(self, runtime_cmd: str) -> RuntimeInfo:
        import shutil
        info = RuntimeInfo(name=runtime_cmd)
        path = shutil.which(runtime_cmd)
        if path:
            info.available = True
            info.path = path
            try:
                import subprocess
                result = subprocess.run([runtime_cmd, "--version"], capture_output=True, text=True, timeout=5)
                version_text = result.stdout.strip() or result.stderr.strip()
                if version_text:
                    info.version = version_text.split("\n")[0][:100]
            except Exception:
                pass
        return info
    def _find_files(self, path: Path, patterns: list[str]) -> list[str]:
        found = []
        for pattern in patterns:
            for f in path.glob(pattern):
                if f.is_file():
                    found.append(str(f.relative_to(path)))
        return sorted(set(found))
    def _confidence_from_evidence(self, env_files: list[str], entrypoints: list[str]) -> float:
        if not env_files and not entrypoints: return 0.0
        score = 0.0
        if env_files: score += min(len(env_files) * 0.3, 0.7)
        if entrypoints: score += min(len(entrypoints) * 0.1, 0.3)
        return min(score, 1.0)
