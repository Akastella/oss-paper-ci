"""C/C++ language adapter."""
from __future__ import annotations
from pathlib import Path
from .base import AdapterBase, AdapterDetection, AdapterPlan, ArtifactRule, SafetyRule, Step

class CppAdapter(AdapterBase):
    @property
    def name(self): return "cpp"
    @property
    def display_name(self): return "C/C++"
    @property
    def aliases(self): return ["c", "c++", "cxx", "cmake"]
    @property
    def ecosystem(self): return "compiled"
    @property
    def supports_execute(self): return True
    @property
    def requires_runtime(self): return ["g++", "gcc", "clang++", "clang"]
    def detect(self, path):
        env_files = self._find_files(path, ["CMakeLists.txt", "Makefile", "configure", "meson.build"])
        source_files = self._find_files(path, ["*.c", "*.cpp", "*.cxx", "*.cc", "*.h", "*.hpp", "src/*.c", "src/*.cpp", "src/*.h"])
        if not env_files and not source_files: return None
        all_evidence = sorted(set(env_files + source_files[:10]))
        confidence = self._confidence_from_evidence(env_files, source_files)
        runtime = self._check_runtime_available("g++")
        if not runtime.available: runtime = self._check_runtime_available("gcc")
        if not runtime.available: runtime = self._check_runtime_available("clang++")
        limitations = []
        if not runtime.available: limitations.append("C/C++ compiler must be installed separately.")
        return AdapterDetection(name=self.name, display_name=self.display_name, confidence=confidence, evidence=all_evidence, runtime=runtime, supports_dry_run=True, supports_execute=runtime.available, limitations=limitations)
    def plan(self, path):
        install_steps, run_steps, warnings, notes = [], [], [], []
        if self._find_files(path, ["CMakeLists.txt"]):
            install_steps.append(Step(command="cmake -S . -B build", description="Configure CMake"))
            install_steps.append(Step(command="cmake --build build", description="Build with CMake"))
            run_steps.append(Step(command="cd build && ctest --output-on-failure", description="Run CMake tests"))
        elif self._find_files(path, ["Makefile"]):
            install_steps.append(Step(command="make", description="Build with Make"))
            run_steps.append(Step(command="make test", description="Run Make tests"))
        elif self._find_files(path, ["configure"]):
            install_steps.append(Step(command="./configure", description="Run configure"))
            install_steps.append(Step(command="make", description="Build with Make"))
        else:
            warnings.append("No C/C++ build configuration found")
        return AdapterPlan(adapter_name=self.name, install_steps=install_steps, run_steps=run_steps, steps=install_steps + run_steps, warnings=warnings, notes=notes)
    def artifact_rules(self, path):
        return [ArtifactRule(pattern="build/**", description="Build directory"), ArtifactRule(pattern="build/bin/*", description="Binaries")]
    def safety_rules(self, path):
        return [SafetyRule(rule_type="block_command", pattern="rm -rf /", message="Recursive delete blocked", severity="error")]
