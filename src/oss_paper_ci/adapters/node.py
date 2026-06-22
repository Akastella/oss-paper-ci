"""Node.js language adapter."""
from __future__ import annotations
from pathlib import Path
from .base import AdapterBase, AdapterDetection, AdapterPlan, ArtifactRule, SafetyRule, Step

class NodeAdapter(AdapterBase):
    @property
    def name(self): return "node"
    @property
    def display_name(self): return "Node.js"
    @property
    def aliases(self): return ["nodejs", "javascript", "js", "ts", "typescript"]
    @property
    def ecosystem(self): return "scripting"
    @property
    def supports_execute(self): return True
    @property
    def requires_runtime(self): return ["node"]
    def detect(self, path):
        env_files = self._find_files(path, ["package.json", "package-lock.json", "yarn.lock", "pnpm-lock.yaml"])
        entrypoints = self._find_files(path, ["scripts/*.js", "scripts/*.ts", "src/*.js", "index.js", "main.js"])
        if not env_files and not entrypoints: return None
        all_evidence = sorted(set(env_files + entrypoints[:5]))
        confidence = self._confidence_from_evidence(env_files, entrypoints)
        runtime = self._check_runtime_available("node")
        limitations = []
        if not runtime.available: limitations.append("Node.js runtime must be installed separately.")
        return AdapterDetection(name=self.name, display_name=self.display_name, confidence=confidence, evidence=all_evidence, runtime=runtime, supports_dry_run=True, supports_execute=runtime.available, limitations=limitations)
    def plan(self, path):
        install_steps, run_steps, warnings, notes = [], [], [], []
        lock_files = self._find_files(path, ["pnpm-lock.yaml", "yarn.lock", "package-lock.json"])
        if any("pnpm-lock" in f for f in lock_files):
            install_steps.append(Step(command="pnpm install", description="Install with pnpm", requires_network=True))
        elif any("yarn.lock" in f for f in lock_files):
            install_steps.append(Step(command="yarn install", description="Install with yarn", requires_network=True))
        elif any("package-lock.json" in f for f in lock_files):
            install_steps.append(Step(command="npm ci", description="Install with npm ci", requires_network=True))
        elif self._find_files(path, ["package.json"]):
            install_steps.append(Step(command="npm install", description="Install with npm", requires_network=True))
        entrypoints = self._find_files(path, ["scripts/*.js", "scripts/*.ts", "index.js", "main.js"])
        for ep in entrypoints[:3]:
            run_steps.append(Step(command=f"node {ep}", description=f"Run {ep}"))
        if not run_steps: warnings.append("No Node.js entrypoints found")
        return AdapterPlan(adapter_name=self.name, install_steps=install_steps, run_steps=run_steps, steps=install_steps + run_steps, warnings=warnings, notes=notes)
    def artifact_rules(self, path):
        return [ArtifactRule(pattern="output/**", description="Output"), ArtifactRule(pattern="dist/**", description="Build output")]
    def safety_rules(self, path):
        return [SafetyRule(rule_type="warn", pattern="npm install", message="npm install downloads packages", severity="warning")]
