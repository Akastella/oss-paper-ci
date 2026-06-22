"""Adapter registry for language adapter discovery and management."""
from __future__ import annotations
from pathlib import Path
from typing import Any
from .base import AdapterBase, AdapterDetection, AdapterPlan

class AdapterRegistry:
    def __init__(self) -> None:
        self._adapters: dict[str, AdapterBase] = {}
        self._aliases: dict[str, str] = {}
    def register(self, adapter: AdapterBase) -> None:
        self._adapters[adapter.name] = adapter
        for alias in adapter.aliases:
            self._aliases[alias.lower()] = adapter.name
    def get(self, name: str) -> AdapterBase | None:
        name_lower = name.lower()
        if name_lower in self._adapters: return self._adapters[name_lower]
        alias_target = self._aliases.get(name_lower)
        if alias_target: return self._adapters.get(alias_target)
        return None
    def list_adapters(self) -> list[dict[str, Any]]:
        result = []
        for name in sorted(self._adapters.keys()):
            adapter = self._adapters[name]
            result.append({"name": adapter.name, "display_name": adapter.display_name, "aliases": sorted(adapter.aliases), "ecosystem": adapter.ecosystem, "supports_dry_run": adapter.supports_dry_run, "supports_execute": adapter.supports_execute, "requires_runtime": adapter.requires_runtime})
        return result
    def detect(self, path: Path) -> list[AdapterDetection]:
        detections: list[AdapterDetection] = []
        for adapter in self._adapters.values():
            detection = adapter.detect(path)
            if detection is not None:
                detections.append(detection)
        detections.sort(key=lambda d: d.confidence, reverse=True)
        return detections
    def detect_best(self, path: Path) -> AdapterDetection | None:
        detections = self.detect(path)
        return detections[0] if detections else None
    def plan(self, path: Path, adapter_name: str | None = None) -> AdapterPlan:
        if adapter_name:
            adapter = self.get(adapter_name)
            if not adapter: raise ValueError(f"Unknown adapter: {adapter_name}")
        else:
            detection = self.detect_best(path)
            if not detection: raise ValueError("No adapter detected for this repository")
            adapter = self.get(detection.name)
            if not adapter: raise ValueError(f"Adapter not found: {detection.name}")
        return adapter.plan(path)
    def get_adapter_names(self) -> list[str]:
        return sorted(self._adapters.keys())

_registry: AdapterRegistry | None = None

def get_registry() -> AdapterRegistry:
    global _registry
    if _registry is None:
        _registry = AdapterRegistry()
        _register_all(_registry)
    return _registry

def _register_all(registry: AdapterRegistry) -> None:
    from .python import PythonAdapter
    from .r import RAdapter
    from .julia import JuliaAdapter
    from .matlab import MatlabAdapter
    from .node import NodeAdapter
    from .rust import RustAdapter
    from .java import JavaAdapter
    from .cpp import CppAdapter
    from .make import MakeAdapter
    from .snakemake import SnakemakeAdapter
    from .nextflow import NextflowAdapter
    from .shell import ShellAdapter
    for adapter in [PythonAdapter(), RAdapter(), JuliaAdapter(), MatlabAdapter(), NodeAdapter(), RustAdapter(), JavaAdapter(), CppAdapter(), MakeAdapter(), SnakemakeAdapter(), NextflowAdapter(), ShellAdapter()]:
        registry.register(adapter)

def reset_registry() -> None:
    global _registry
    _registry = None
