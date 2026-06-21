"""Tests for the extended reproducibility schema v0.2."""

import pytest
from pathlib import Path

from oss_paper_ci.repro_schema import (
    OrchestratorContract,
    load_orchestrator_contract,
    validate_orchestrator_schema,
)


DEMO_CONTRACT = "examples/repro-system-demo/reproducibility.yml"


class TestOrchestratorSchema:
    """Tests for schema loading and validation."""

    def test_load_demo_contract(self):
        contract = load_orchestrator_contract(DEMO_CONTRACT)
        assert contract.schema_version == "0.2"
        assert contract.project_name == "repro-system-demo"
        assert len(contract.commands) == 3
        assert contract.commands[0].id == "train"
        assert contract.commands[1].id == "evaluate"
        assert contract.commands[2].id == "make_figures"

    def test_command_dependencies(self):
        contract = load_orchestrator_contract(DEMO_CONTRACT)
        assert contract.commands[1].depends_on == ["train"]
        assert contract.commands[2].depends_on == ["evaluate"]

    def test_artifacts(self):
        contract = load_orchestrator_contract(DEMO_CONTRACT)
        assert len(contract.artifacts) == 3
        assert contract.artifacts[0].path == "results/model.json"

    def test_metrics(self):
        contract = load_orchestrator_contract(DEMO_CONTRACT)
        assert len(contract.metrics) == 2
        assert contract.metrics[0].key == "accuracy"
        assert contract.metrics[0].expected_min == 0.0
        assert contract.metrics[0].expected_max == 1.0

    def test_safety(self):
        contract = load_orchestrator_contract(DEMO_CONTRACT)
        assert contract.safety.network is False
        assert contract.safety.allow_shell is False
        assert contract.safety.max_runtime_seconds == 120

    def test_backward_compat_old_format(self, tmp_path):
        """Old format without schema_version should load with defaults."""
        (tmp_path / "reproducibility.yml").write_text(
            'version: "0.3"\n'
            'project_name: "old-project"\n'
            'experiments:\n'
            '  - id: train\n'
            '    command: python train.py\n'
            '    timeout_seconds: 60\n',
            encoding="utf-8",
        )
        contract = load_orchestrator_contract(str(tmp_path / "reproducibility.yml"))
        assert contract.schema_version == "0.1"
        assert len(contract.commands) == 1
        assert contract.commands[0].run == "python train.py"

    def test_validate_schema(self):
        import yaml
        with open(DEMO_CONTRACT, encoding="utf-8") as f:
            data = yaml.safe_load(f)
        warnings = validate_orchestrator_schema(data)
        assert len(warnings) == 0

    def test_validate_missing_command_id(self):
        warnings = validate_orchestrator_schema({
            "commands": [{"run": "python train.py"}]
        })
        assert any("id" in w for w in warnings)

    def test_validate_missing_command_run(self):
        warnings = validate_orchestrator_schema({
            "commands": [{"id": "train"}]
        })
        assert any("run" in w for w in warnings)

    def test_validate_duplicate_ids(self):
        warnings = validate_orchestrator_schema({
            "commands": [
                {"id": "train", "run": "python a.py"},
                {"id": "train", "run": "python b.py"},
            ]
        })
        assert any("unique" in w for w in warnings)
