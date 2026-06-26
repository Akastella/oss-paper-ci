"""Reproducibility DSL v1: formal schema for declaring and planning reproduction workflows."""

from .schema import (
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
from .loader import load_dsl, load_dsl_raw
from .validator import validate_dsl, ValidationResult, ValidationFinding
from .normalizer import normalize_dsl, normalize_dsl_json
from .migration import migrate_legacy, migrate_legacy_with_report, MigrationReport
from .dag import DAG, DAGNode, build_dag
from .planner import ExecutionPlan, PlanStep, plan_execution
from .safety import SafetyReport, check_command_safety, check_dsl_safety
from .report import (
    format_validation_report,
    format_plan_report,
    format_dag_dot,
    format_dag_html,
    format_normalized_json,
    format_migration_report,
    format_safety_report,
)

__all__ = [
    # Schema
    "ReproDSL",
    "ProjectSpec",
    "EnvironmentSpec",
    "DatasetSpec",
    "StepSpec",
    "ArtifactSpec",
    "MetricSpec",
    "ExpectedSpec",
    "SafetySpec",
    "MetricKeySpec",
    # Loader
    "load_dsl",
    "load_dsl_raw",
    # Validator
    "validate_dsl",
    "ValidationResult",
    "ValidationFinding",
    # Normalizer
    "normalize_dsl",
    "normalize_dsl_json",
    # Migration
    "migrate_legacy",
    "migrate_legacy_with_report",
    "MigrationReport",
    # DAG
    "DAG",
    "DAGNode",
    "build_dag",
    # Planner
    "ExecutionPlan",
    "PlanStep",
    "plan_execution",
    # Safety
    "SafetyReport",
    "check_command_safety",
    "check_dsl_safety",
    # Report
    "format_validation_report",
    "format_plan_report",
    "format_dag_dot",
    "format_dag_html",
    "format_normalized_json",
    "format_migration_report",
    "format_safety_report",
]
