"""Java language adapter."""
from __future__ import annotations
from pathlib import Path
from .base import AdapterBase, AdapterDetection, AdapterPlan, ArtifactRule, SafetyRule, Step

class JavaAdapter(AdapterBase):
    @property
    def name(self): return "java"
    @property
    def display_name(self): return "Java"
    @property
    def aliases(self): return ["maven", "gradle", "jvm"]
    @property
    def ecosystem(self): return "compiled"
    @property
    def supports_execute(self): return True
    @property
    def requires_runtime(self): return ["java"]
    def detect(self, path):
        env_files = self._find_files(path, ["pom.xml", "build.gradle", "build.gradle.kts", "settings.gradle", "gradlew"])
        entrypoints = self._find_files(path, ["src/main/java/**/*.java"])
        if not env_files: return None
        all_evidence = sorted(set(env_files + entrypoints[:5]))
        confidence = self._confidence_from_evidence(env_files, entrypoints)
        runtime = self._check_runtime_available("java")
        limitations = []
        if not runtime.available: limitations.append("Java runtime must be installed separately.")
        return AdapterDetection(name=self.name, display_name=self.display_name, confidence=confidence, evidence=all_evidence, runtime=runtime, supports_dry_run=True, supports_execute=runtime.available, limitations=limitations)
    def plan(self, path):
        install_steps, run_steps, warnings, notes = [], [], [], []
        if self._find_files(path, ["pom.xml"]):
            install_steps.append(Step(command="mvn package -DskipTests", description="Build with Maven", requires_network=True))
            run_steps.append(Step(command="mvn test", description="Run Maven tests"))
        elif self._find_files(path, ["build.gradle", "build.gradle.kts"]):
            gradle = "./gradlew" if self._find_files(path, ["gradlew"]) else "gradle"
            install_steps.append(Step(command=f"{gradle} build -x test", description="Build with Gradle", requires_network=True))
            run_steps.append(Step(command=f"{gradle} test", description="Run Gradle tests"))
        else:
            warnings.append("No Java build configuration found")
        return AdapterPlan(adapter_name=self.name, install_steps=install_steps, run_steps=run_steps, steps=install_steps + run_steps, warnings=warnings, notes=notes)
    def artifact_rules(self, path):
        return [ArtifactRule(pattern="target/*.jar", description="JAR artifacts"), ArtifactRule(pattern="build/libs/*.jar", description="Gradle JARs")]
    def safety_rules(self, path):
        return [SafetyRule(rule_type="warn", pattern="mvn install", message="mvn install modifies local repo", severity="warning")]
