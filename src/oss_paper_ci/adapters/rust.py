"""Rust language adapter."""
from __future__ import annotations
from pathlib import Path
from .base import AdapterBase, AdapterDetection, AdapterPlan, ArtifactRule, SafetyRule, Step

class RustAdapter(AdapterBase):
    @property
    def name(self): return "rust"
    @property
    def display_name(self): return "Rust"
    @property
    def aliases(self): return ["cargo", "rs"]
    @property
    def ecosystem(self): return "compiled"
    @property
    def supports_execute(self): return True
    @property
    def requires_runtime(self): return ["cargo"]
    def detect(self, path):
        env_files = self._find_files(path, ["Cargo.toml", "Cargo.lock"])
        entrypoints = self._find_files(path, ["src/main.rs", "src/bin/*.rs", "src/lib.rs"])
        if not env_files: return None
        all_evidence = sorted(set(env_files + entrypoints[:5]))
        confidence = self._confidence_from_evidence(env_files, entrypoints)
        runtime = self._check_runtime_available("cargo")
        limitations = []
        if not runtime.available: limitations.append("Rust toolchain must be installed separately.")
        return AdapterDetection(name=self.name, display_name=self.display_name, confidence=confidence, evidence=all_evidence, runtime=runtime, supports_dry_run=True, supports_execute=runtime.available, limitations=limitations)
    def plan(self, path):
        install_steps, run_steps, warnings, notes = [], [], [], []
        if self._find_files(path, ["Cargo.toml"]):
            install_steps.append(Step(command="cargo build --release", description="Build Rust project", requires_network=True))
            run_steps.append(Step(command="cargo run --release", description="Run Rust project"))
            run_steps.append(Step(command="cargo test", description="Run Rust tests"))
        else:
            warnings.append("No Rust project found")
        return AdapterPlan(adapter_name=self.name, install_steps=install_steps, run_steps=run_steps, steps=install_steps + run_steps, warnings=warnings, notes=notes)
    def artifact_rules(self, path):
        return [ArtifactRule(pattern="target/release/*", description="Release binaries")]
    def safety_rules(self, path):
        return [SafetyRule(rule_type="warn", pattern="cargo install", message="cargo install downloads crates", severity="warning")]
