"""Reproducibility dossier builder.

Generates a structured reproducibility dossier from scan, reproduce,
or capsule reports. The dossier contains evidence map, risk register,
remediation plan, and audience-specific outputs.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from oss_paper_ci import __version__
from oss_paper_ci.evidence_map import (
    EvidenceItem,
    build_evidence_map_from_reproduce,
    build_evidence_map_from_scan,
)
from oss_paper_ci.i18n_templates import get_all_templates, get_template
from oss_paper_ci.remediation import (
    RemediationItem,
    RiskItem,
    build_remediation_from_reproduce,
    build_remediation_from_scan,
    build_risk_register_from_scan,
)


@dataclass
class Dossier:
    """A reproducibility dossier."""

    schema_version: str = "0.1"
    dossier_type: str = "oss-paper-ci-reproducibility-dossier"
    created_by: str = "oss-paper-ci"
    oss_paper_ci_version: str = __version__
    audience: str = "author"
    language: str = "en"
    source: dict[str, str] = field(default_factory=dict)
    executive_summary: dict[str, Any] = field(default_factory=dict)
    evidence_map: list[EvidenceItem] = field(default_factory=list)
    risk_register: list[RiskItem] = field(default_factory=list)
    remediation_plan: list[RemediationItem] = field(default_factory=list)
    audience_notes: list[str] = field(default_factory=list)
    next_steps: list[str] = field(default_factory=list)
    non_claims: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema_version": self.schema_version,
            "dossier_type": self.dossier_type,
            "created_by": self.created_by,
            "oss_paper_ci_version": self.oss_paper_ci_version,
            "audience": self.audience,
            "language": self.language,
            "source": self.source,
            "executive_summary": self.executive_summary,
            "evidence_map": [e.to_dict() for e in self.evidence_map],
            "risk_register": [r.to_dict() for r in self.risk_register],
            "remediation_plan": [r.to_dict() for r in self.remediation_plan],
            "audience_notes": self.audience_notes,
            "next_steps": self.next_steps,
            "non_claims": self.non_claims,
        }


def build_dossier(
    *,
    scan_report: str | None = None,
    reproduce_report: str | None = None,
    capsule: str | None = None,
    workspace_report: str | None = None,
    repo_path: str | None = None,
    audience: str = "author",
    language: str = "en",
) -> Dossier:
    """Build a reproducibility dossier.

    Args:
        scan_report: Path to scan JSON report.
        reproduce_report: Path to reproduce JSON report.
        capsule: Path to capsule zip.
        workspace_report: Path to workspace/batch JSON report.
        repo_path: Path to repository (for on-the-fly scan).
        audience: Target audience (author, reviewer, maintainer).
        language: Output language (en, zh-CN, ja).

    Returns:
        Dossier object.
    """
    dossier = Dossier(audience=audience, language=language)
    tmpl = get_all_templates(language)

    # Load scan data
    scan_data = None
    if scan_report:
        scan_data = _load_json(scan_report)
        dossier.source["scan_report"] = scan_report
    elif repo_path:
        # Run a lightweight scan
        try:
            from oss_paper_ci.scanner import scan as run_scan
            from oss_paper_ci.reporting.json_report import generate_json_report
            import tempfile
            report = run_scan(repo_path)
            scan_data = json.loads(generate_json_report(report))
            dossier.source["repo"] = repo_path
        except Exception:
            pass

    # Load reproduce data
    reproduce_data = None
    if reproduce_report:
        reproduce_data = _load_json(reproduce_report)
        dossier.source["reproduce_report"] = reproduce_report

    # Build evidence map
    if scan_data:
        dossier.evidence_map.extend(build_evidence_map_from_scan(scan_data))
    if reproduce_data:
        dossier.evidence_map.extend(build_evidence_map_from_reproduce(reproduce_data))

    # Build risk register
    if scan_data:
        dossier.risk_register.extend(build_risk_register_from_scan(scan_data))

    # Build remediation plan
    if scan_data:
        dossier.remediation_plan.extend(build_remediation_from_scan(scan_data))
    if reproduce_data:
        dossier.remediation_plan.extend(build_remediation_from_reproduce(reproduce_data))

    # Sort remediation by priority
    priority_order = {"P0": 0, "P1": 1, "P2": 2, "P3": 3}
    dossier.remediation_plan.sort(key=lambda x: priority_order.get(x.priority, 9))

    # Build executive summary
    score = None
    status = "unknown"
    if scan_data:
        summary = scan_data.get("summary", {})
        score = summary.get("score")
        status = summary.get("status", "unknown")

    confidence = "low"
    if score is not None:
        if score >= 80:
            confidence = "high"
        elif score >= 50:
            confidence = "medium"

    status_map = {
        "pass": tmpl["status_ready"],
        "warn": tmpl["status_needs_work"],
        "fail": tmpl["status_blocked"],
    }

    plain_language = _build_plain_language(
        scan_data, reproduce_data, audience, language, score, status
    )

    dossier.executive_summary = {
        "plain_language": plain_language,
        "status": status_map.get(status, tmpl["status_unknown"]),
        "confidence": tmpl[f"confidence_{confidence}"],
        "score": score,
        "limitations": [
            tmpl["disclaimer"],
        ],
    }

    # Audience-specific notes
    dossier.audience_notes = _build_audience_notes(audience, language, dossier)

    # Next steps
    dossier.next_steps = _build_next_steps(audience, language, dossier)

    # Non-claims
    dossier.non_claims = [
        tmpl["disclaimer"],
    ]

    return dossier


def _load_json(path: str) -> dict[str, Any] | None:
    """Load a JSON file."""
    try:
        return json.loads(Path(path).read_text(encoding="utf-8"))
    except Exception:
        return None


def _build_plain_language(
    scan_data: dict | None,
    reproduce_data: dict | None,
    audience: str,
    language: str,
    score: int | None,
    status: str,
) -> str:
    """Build plain-language executive summary."""
    tmpl = get_all_templates(language)

    parts = []

    if score is not None:
        if language == "zh-CN":
            parts.append(f"仓库复现准备度评分：{score}/100。")
        elif language == "ja":
            parts.append(f"リポジトリの再現準備度スコア：{score}/100。")
        else:
            parts.append(f"Repository reproducibility readiness score: {score}/100.")

    if status == "pass":
        if language == "zh-CN":
            parts.append("仓库已通过基本复现准备度检查。")
        elif language == "ja":
            parts.append("リポジトリは基本的な再現準備度チェックを通過しました。")
        else:
            parts.append("The repository passed basic reproducibility readiness checks.")
    elif status == "fail":
        if language == "zh-CN":
            parts.append("仓库存在阻塞性复现问题，需要修复。")
        elif language == "ja":
            parts.append("リポジトリにブロッキングな再現問題があり、修正が必要です。")
        else:
            parts.append("The repository has blocking reproducibility issues that need to be addressed.")
    elif status == "warn":
        if language == "zh-CN":
            parts.append("仓库有复现相关警告，建议改进。")
        elif language == "ja":
            parts.append("リポジトリに再現に関する警告があり、改善が推奨されます。")
        else:
            parts.append("The repository has reproducibility warnings. Improvements are recommended.")

    if reproduce_data:
        from oss_paper_ci.guidance import get_plain_language_summary
        mode = "execute" if not reproduce_data.get("dry_run", True) else "dry-run"
        summary = get_plain_language_summary(
            mode=mode,
            commands_attempted=len(reproduce_data.get("command_results", [])),
            commands_succeeded=sum(1 for r in reproduce_data.get("command_results", []) if r.get("exit_code") == 0),
            commands_failed=sum(1 for r in reproduce_data.get("command_results", []) if r.get("exit_code", 0) != 0 and not r.get("blocked")),
            scan_score=score,
            scan_status=status,
        )
        parts.append(summary)

    return " ".join(parts) if parts else tmpl["disclaimer"]


def _build_audience_notes(audience: str, language: str, dossier: Dossier) -> list[str]:
    """Build audience-specific notes."""
    tmpl = get_all_templates(language)
    notes = []

    if audience == "author":
        notes.append(tmpl["author_intro"])
        blocking = [r for r in dossier.remediation_plan if r.blocking]
        if blocking:
            if language == "zh-CN":
                notes.append(f"有 {len(blocking)} 个阻塞问题需要优先修复。")
            elif language == "ja":
                notes.append(f"優先的に修正すべきブロッキング問題が{len(blocking)}件あります。")
            else:
                notes.append(f"There are {len(blocking)} blocking issues that should be addressed first.")
    elif audience == "reviewer":
        notes.append(tmpl["reviewer_intro"])
        if language == "zh-CN":
            notes.append("本摘要不提供录用/拒稿建议。请结合领域知识和同行评议标准综合判断。")
        elif language == "ja":
            notes.append("このサマリーは採択/拒否の推奨を提供しません。分野知識と査読基準に基づいて総合的に判断してください。")
        else:
            notes.append("This summary does not make accept/reject recommendations. Use your domain expertise and peer review standards.")
    elif audience == "maintainer":
        notes.append(tmpl["maintainer_intro"])
        if language == "zh-CN":
            notes.append("建议使用 workspace 和 batch scan 进行批量治理。")
        elif language == "ja":
            notes.append("workspace と batch scan を使用した一括ガバナンスを推奨します。")
        else:
            notes.append("Consider using workspace and batch scan for organization-wide governance.")

    return notes


def _build_next_steps(audience: str, language: str, dossier: Dossier) -> list[str]:
    """Build next steps."""
    steps = []

    if audience == "author":
        for item in dossier.remediation_plan[:3]:
            if language == "zh-CN":
                steps.append(f"[{item.priority}] {item.action}")
            elif language == "ja":
                steps.append(f"[{item.priority}] {item.action}")
            else:
                steps.append(f"[{item.priority}] {item.action}")
    elif audience == "reviewer":
        if language == "zh-CN":
            steps.append("检查证据清单中的缺失项")
            steps.append("评估风险登记中的严重程度")
            steps.append("参考整改计划了解作者可以做什么")
        elif language == "ja":
            steps.append("エビデンスマップの欠落項目を確認")
            steps.append("リスクレジスタの深刻度を評価")
            steps.append("改善計画を参考に著者が何ができるかを確認")
        else:
            steps.append("Review missing items in the evidence map")
            steps.append("Assess severity in the risk register")
            steps.append("Use the remediation plan to understand what the author can do")
    elif audience == "maintainer":
        if language == "zh-CN":
            steps.append("设置 policy profile 和最低分数阈值")
            steps.append("使用 workspace 批量扫描多个仓库")
            steps.append("定期运行 baseline compare 检测退化")
        elif language == "ja":
            steps.append("ポリシープロファイルと最低スコア閾値を設定")
            steps.append("workspace で複数リポジトリを一括スキャン")
            steps.append("定期的に baseline compare で退化を検出")
        else:
            steps.append("Set up policy profiles and minimum score thresholds")
            steps.append("Use workspace to batch scan multiple repositories")
            steps.append("Run baseline compare regularly to detect regressions")

    return steps
