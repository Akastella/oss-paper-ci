"""Tests for repro_dsl.schema -- dataclass creation, to_dict, to_json, dag_hash."""
from __future__ import annotations

import json
import pytest
from oss_paper_ci.repro_dsl.schema import (
    ReproDSL,
    ProjectSpec,
    EnvironmentSpec,
    DatasetSpec,
    StepSpec,
    ArtifactSpec,
    MetricSpec,
    ExpectedSpec,
    SafetySpec,
    MetricKeySpec,
)


class TestProjectSpec:
    def test_minimal_creation(self):
        p = ProjectSpec(name="test")
        assert p.name == "test"
        assert p.description == ""
        assert p.paper == ""
        assert p.repository == ""

    def test_full_creation(self):
        p = ProjectSpec(name="my-paper", description="desc", paper="arxiv:1234", repository="https://github.com/x/y")
        assert p.name == "my-paper"
        assert p.paper == "arxiv:1234"

    def test_to_dict_minimal(self):
        p = ProjectSpec(name="test")
        d = p.to_dict()
        assert d == {"name": "test"}

    def test_to_dict_full(self):
        p = ProjectSpec(name="x", description="d", paper="p", repository="r")
        d = p.to_dict()
        assert d["name"] == "x"
        assert d["description"] == "d"
        assert d["paper"] == "p"
        assert d["repository"] == "r"

    def test_frozen(self):
        p = ProjectSpec(name="x")
        with pytest.raises(AttributeError):
            p.name = "y"  # type: ignore[misc]


class TestEnvironmentSpec:
    def test_defaults(self):
        e = EnvironmentSpec()
        assert e.adapter == ""
        assert e.runtime == ""
        assert e.python == ""
        assert e.install == []

    def test_to_dict_empty(self):
        e = EnvironmentSpec()
        assert e.to_dict() == {}

    def test_to_dict_with_values(self):
        e = EnvironmentSpec(adapter="python", runtime="python", python=">=3.10", install=["requirements.txt"])
        d = e.to_dict()
        assert d["adapter"] == "python"
        assert d["python"] == ">=3.10"
        assert d["install"] == ["requirements.txt"]


class TestDatasetSpec:
    def test_defaults(self):
        ds = DatasetSpec(path="data/")
        assert ds.required is True
        assert ds.description == ""

    def test_to_dict(self):
        ds = DatasetSpec(path="data/", required=False, description="test data")
        d = ds.to_dict()
        assert d["path"] == "data/"
        assert d["required"] is False
        assert d["description"] == "test data"


class TestStepSpec:
    def test_defaults(self):
        s = StepSpec(id="s1", command="echo hello")
        assert s.adapter == ""
        assert s.needs == []
        assert s.produces == []
        assert s.timeout == 3600
        assert s.metrics == []
        assert s.description == ""

    def test_to_dict_minimal(self):
        s = StepSpec(id="s1", command="echo hello")
        d = s.to_dict()
        assert d == {"id": "s1", "command": "echo hello"}

    def test_to_dict_with_needs_sorted(self):
        s = StepSpec(id="s1", command="echo", needs=["c", "a", "b"])
        d = s.to_dict()
        assert d["needs"] == ["a", "b", "c"]

    def test_to_dict_timeout_default_omitted(self):
        s = StepSpec(id="s1", command="echo", timeout=3600)
        d = s.to_dict()
        assert "timeout" not in d

    def test_to_dict_timeout_non_default_included(self):
        s = StepSpec(id="s1", command="echo", timeout=60)
        d = s.to_dict()
        assert d["timeout"] == 60


class TestMetricKeySpec:
    def test_creation(self):
        mk = MetricKeySpec(path="results/metrics.json", keys=["accuracy", "f1"])
        assert mk.path == "results/metrics.json"
        assert mk.keys == ["accuracy", "f1"]

    def test_to_dict_sorts_keys(self):
        mk = MetricKeySpec(path="m.json", keys=["z", "a", "m"])
        d = mk.to_dict()
        assert d["keys"] == ["a", "m", "z"]


class TestMetricSpec:
    def test_defaults(self):
        m = MetricSpec(key="accuracy")
        assert m.min is None
        assert m.max is None

    def test_to_dict_with_bounds(self):
        m = MetricSpec(key="accuracy", min=0.0, max=1.0)
        d = m.to_dict()
        assert d == {"key": "accuracy", "min": 0.0, "max": 1.0}

    def test_to_dict_min_only(self):
        m = MetricSpec(key="loss", max=10.0)
        d = m.to_dict()
        assert "min" not in d
        assert d["max"] == 10.0


class TestExpectedSpec:
    def test_empty(self):
        e = ExpectedSpec()
        assert e.to_dict() == {}

    def test_with_metrics(self):
        e = ExpectedSpec(metrics={"accuracy": MetricSpec(key="accuracy", min=0.8)})
        d = e.to_dict()
        assert "metrics" in d
        assert "accuracy" in d["metrics"]


class TestSafetySpec:
    def test_defaults_all_false(self):
        s = SafetySpec()
        assert s.network is False
        assert s.allow_install is False
        assert s.allow_gpu is False

    def test_to_dict(self):
        s = SafetySpec(network=True, allow_install=False, allow_gpu=True)
        d = s.to_dict()
        assert d == {"network": True, "allow_install": False, "allow_gpu": True}


class TestArtifactSpec:
    def test_defaults(self):
        a = ArtifactSpec(path="results/model.json")
        assert a.type == "file"

    def test_to_dict(self):
        a = ArtifactSpec(path="figures/", type="directory")
        d = a.to_dict()
        assert d == {"path": "figures/", "type": "directory"}


class TestReproDSL:
    def _make_dsl(self) -> ReproDSL:
        return ReproDSL(
            project=ProjectSpec(name="test-project"),
            steps={
                "train": StepSpec(id="train", command="python train.py", produces=["model.pkl"]),
                "eval": StepSpec(id="eval", command="python eval.py", needs=["train"]),
            },
            safety=SafetySpec(),
        )

    def test_creation(self):
        dsl = self._make_dsl()
        assert dsl.version == 1
        assert dsl.project.name == "test-project"
        assert len(dsl.steps) == 2

    def test_to_dict_structure(self):
        dsl = self._make_dsl()
        d = dsl.to_dict()
        assert d["version"] == 1
        assert "project" in d
        assert "steps" in d
        assert "safety" in d

    def test_to_dict_steps_sorted(self):
        dsl = ReproDSL(
            project=ProjectSpec(name="p"),
            steps={
                "z_step": StepSpec(id="z_step", command="echo z"),
                "a_step": StepSpec(id="a_step", command="echo a"),
            },
            safety=SafetySpec(),
        )
        d = dsl.to_dict()
        keys = list(d["steps"].keys())
        assert keys == ["a_step", "z_step"]

    def test_to_json_is_valid_json(self):
        dsl = self._make_dsl()
        j = dsl.to_json()
        parsed = json.loads(j)
        assert parsed["version"] == 1

    def test_to_json_ends_with_newline(self):
        dsl = self._make_dsl()
        assert dsl.to_json().endswith("\n")

    def test_dag_hash_deterministic(self):
        dsl = self._make_dsl()
        h1 = dsl.dag_hash()
        h2 = dsl.dag_hash()
        assert h1 == h2

    def test_dag_hash_is_hex_string(self):
        dsl = self._make_dsl()
        h = dsl.dag_hash()
        assert len(h) == 16
        int(h, 16)  # should not raise

    def test_dag_hash_changes_with_steps(self):
        dsl1 = ReproDSL(
            project=ProjectSpec(name="p"),
            steps={"a": StepSpec(id="a", command="echo a")},
            safety=SafetySpec(),
        )
        dsl2 = ReproDSL(
            project=ProjectSpec(name="p"),
            steps={"a": StepSpec(id="a", command="echo DIFFERENT")},
            safety=SafetySpec(),
        )
        assert dsl1.dag_hash() != dsl2.dag_hash()

    def test_dag_hash_independent_of_project_name(self):
        """dag_hash only depends on steps+dependencies, not project metadata."""
        dsl1 = ReproDSL(
            project=ProjectSpec(name="project-A"),
            steps={"a": StepSpec(id="a", command="echo a")},
            safety=SafetySpec(),
        )
        dsl2 = ReproDSL(
            project=ProjectSpec(name="project-B"),
            steps={"a": StepSpec(id="a", command="echo a")},
            safety=SafetySpec(),
        )
        assert dsl1.dag_hash() == dsl2.dag_hash()

    def test_default_safety_all_false(self):
        dsl = ReproDSL(project=ProjectSpec(name="p"))
        assert dsl.safety.network is False
        assert dsl.safety.allow_install is False
        assert dsl.safety.allow_gpu is False

    def test_empty_steps(self):
        dsl = ReproDSL(project=ProjectSpec(name="p"))
        assert dsl.steps == {}
        d = dsl.to_dict()
        assert "steps" not in d  # empty steps omitted from to_dict
