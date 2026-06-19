"""Evaluation runner for oss-paper-ci benchmark corpus."""

from __future__ import annotations

import json
import subprocess
from pathlib import Path
from typing import Any

import yaml

from oss_paper_ci import __version__


def load_expected_outcomes(corpus_dir: Path) -> dict:
    """Load expected_outcomes.yml from corpus directory.

    Supports two formats:
    - A dict keyed by repo_id
    - A list of dicts, each with a ``repo_id`` key
    """
    outcomes_path = corpus_dir / "expected_outcomes.yml"
    if not outcomes_path.exists():
        return {}
    with open(outcomes_path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f) or {}

    # Normalise list-of-dicts to a dict keyed by repo_id
    if isinstance(data, list):
        return {entry["repo_id"]: entry for entry in data if "repo_id" in entry}
    return data


def discover_repos(corpus_dir: Path) -> list[Path]:
    """Discover evaluation repos in corpus directory."""
    repos: list[Path] = []
    if not corpus_dir.is_dir():
        return repos
    for entry in sorted(corpus_dir.iterdir()):
        if entry.is_dir() and not entry.name.startswith("."):
            # Check if it has a README.md
            if (entry / "README.md").exists():
                repos.append(entry)
            # Handle before/after structure
            for sub in ["before", "after"]:
                sub_path = entry / sub
                if sub_path.is_dir() and (sub_path / "README.md").exists():
                    repos.append(sub_path)
    return repos


def scan_repo(repo_path: Path) -> dict:
    """Run oss-paper-ci scan on a repo and return results."""
    try:
        result = subprocess.run(
            ["oss-paper-ci", "scan", str(repo_path), "--format", "json", "--no-color"],
            capture_output=True,
            text=True,
            timeout=60,
            cwd=str(repo_path),
        )
        if result.returncode == 0 and result.stdout.strip():
            return json.loads(result.stdout)
        else:
            return {
                "error": result.stderr or "Scan failed",
                "returncode": result.returncode,
            }
    except Exception as e:
        return {"error": str(e)}


def detect_ecosystems(repo_path: Path) -> list[str]:
    """Detect language ecosystems in a repo."""
    ecosystems: list[str] = []
    indicators: dict[str, list[str]] = {
        "python": ["requirements.txt", "pyproject.toml", "setup.py", "setup.cfg"],
        "r": ["DESCRIPTION", "renv.lock", ".Rprofile"],
        "julia": ["Project.toml", "Manifest.toml"],
        "node": ["package.json"],
        "make": ["Makefile"],
        "snakemake": ["Snakefile"],
        "cpp": ["CMakeLists.txt", "*.cpp", "*.h"],
        "rust": ["Cargo.toml"],
        "java": ["pom.xml", "build.gradle"],
    }
    for eco, files in indicators.items():
        for f in files:
            if "*" in f:
                if list(repo_path.glob(f)):
                    ecosystems.append(eco)
                    break
            elif (repo_path / f).exists():
                ecosystems.append(eco)
                break
    return ecosystems


def evaluate_repo(repo_path: Path, expected: dict | None = None) -> dict:
    """Evaluate a single repo against expected outcomes."""
    result: dict[str, Any] = {
        "repo_id": repo_path.name,
        "repo_path": str(repo_path),
        "ecosystems": detect_ecosystems(repo_path),
        "scan_result": None,
        "expected": expected or {},
        "comparison": {},
        "status": "unknown",
    }

    # Run scan
    scan = scan_repo(repo_path)
    result["scan_result"] = scan

    # Compare with expected
    if expected:
        exp_ecos = set(expected.get("expected_ecosystems", []))
        actual_ecos = set(result["ecosystems"])
        result["comparison"]["ecosystems_match"] = exp_ecos.issubset(actual_ecos)

        if "expected_status" in expected:
            actual_status = scan.get("status", "unknown")
            result["comparison"]["status_match"] = actual_status == expected["expected_status"]

        if "expected_score_band" in expected:
            score = scan.get("score", 0)
            bands = expected["expected_score_band"]
            if bands and len(bands) == 2:
                result["comparison"]["score_in_band"] = bands[0] <= score <= bands[1]

    # Determine overall status
    comparisons = result.get("comparison", {})
    if not comparisons:
        result["status"] = "evaluated"
    elif all(comparisons.values()):
        result["status"] = "pass"
    elif any(comparisons.values()):
        result["status"] = "partial"
    else:
        result["status"] = "fail"

    return result


def run_evaluation(corpus_dir: Path) -> dict:
    """Run evaluation on entire corpus."""
    outcomes = load_expected_outcomes(corpus_dir)
    repos = discover_repos(corpus_dir)

    results: dict[str, Any] = {
        "version": __version__,
        "corpus_dir": str(corpus_dir),
        "total_repos": len(repos),
        "repos": [],
        "summary": {
            "pass": 0,
            "partial": 0,
            "fail": 0,
            "evaluated": 0,
            "error": 0,
        },
    }

    for repo_path in repos:
        repo_id = repo_path.name
        expected = outcomes.get(repo_id, {})
        eval_result = evaluate_repo(repo_path, expected)
        results["repos"].append(eval_result)

        status = eval_result["status"]
        if status in results["summary"]:
            results["summary"][status] += 1

    return results


def format_json(results: dict) -> str:
    """Format results as JSON."""
    return json.dumps(results, indent=2, ensure_ascii=False)


def format_markdown(results: dict) -> str:
    """Format results as Markdown."""
    lines: list[str] = []
    lines.append("# Evaluation Summary")
    lines.append("")
    lines.append(f"**Version:** {results['version']}")
    lines.append(f"**Corpus:** {results['corpus_dir']}")
    lines.append(f"**Total Repos:** {results['total_repos']}")
    lines.append("")

    lines.append("## Summary")
    lines.append("")
    summary = results["summary"]
    lines.append(f"- Pass: {summary['pass']}")
    lines.append(f"- Partial: {summary['partial']}")
    lines.append(f"- Fail: {summary['fail']}")
    lines.append(f"- Evaluated: {summary['evaluated']}")
    lines.append(f"- Error: {summary['error']}")
    lines.append("")

    lines.append("## Repository Results")
    lines.append("")
    lines.append("| Repo ID | Ecosystems | Status | Score | Expected Status | Match |")
    lines.append("|---------|------------|--------|-------|-----------------|-------|")

    for repo in results["repos"]:
        repo_id = repo["repo_id"]
        ecosystems = ", ".join(repo["ecosystems"]) or "unknown"
        status = repo["status"]
        scan = repo.get("scan_result") or {}
        score = scan.get("score", "N/A")
        exp_status = repo["expected"].get("expected_status", "N/A")
        comparison = repo.get("comparison", {})
        status_match = comparison.get("status_match", "N/A")

        lines.append(
            f"| {repo_id} | {ecosystems} | {status} | {score} | {exp_status} | {status_match} |"
        )

    lines.append("")
    lines.append("---")
    lines.append("*Generated by oss-paper-ci evaluation runner*")

    return "\n".join(lines)


def format_html(results: dict) -> str:
    """Format results as HTML (self-contained, no external CDN)."""
    html_lines: list[str] = []
    html_lines.append("<!DOCTYPE html>")
    html_lines.append("<html lang='en'>")
    html_lines.append("<head>")
    html_lines.append("<meta charset='UTF-8'>")
    html_lines.append("<meta name='viewport' content='width=device-width, initial-scale=1.0'>")
    html_lines.append("<title>Evaluation Summary - oss-paper-ci</title>")
    html_lines.append("<style>")
    html_lines.append("body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; max-width: 900px; margin: 0 auto; padding: 20px; }")
    html_lines.append("table { border-collapse: collapse; width: 100%; }")
    html_lines.append("th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }")
    html_lines.append("th { background-color: #f2f2f2; }")
    html_lines.append("tr:nth-child(even) { background-color: #f9f9f9; }")
    html_lines.append("h1, h2 { color: #333; }")
    html_lines.append(".pass { color: green; } .fail { color: red; } .partial { color: orange; }")
    html_lines.append("</style>")
    html_lines.append("</head>")
    html_lines.append("<body>")
    html_lines.append("<h1>Evaluation Summary</h1>")
    html_lines.append(f"<p><strong>Version:</strong> {results['version']}</p>")
    html_lines.append(f"<p><strong>Total Repos:</strong> {results['total_repos']}</p>")

    html_lines.append("<h2>Summary</h2>")
    summary = results["summary"]
    html_lines.append("<ul>")
    html_lines.append(f"<li>Pass: {summary['pass']}</li>")
    html_lines.append(f"<li>Partial: {summary['partial']}</li>")
    html_lines.append(f"<li>Fail: {summary['fail']}</li>")
    html_lines.append("</ul>")

    html_lines.append("<h2>Repository Results</h2>")
    html_lines.append("<table>")
    html_lines.append("<tr><th>Repo ID</th><th>Ecosystems</th><th>Status</th><th>Score</th></tr>")

    for repo in results["repos"]:
        status_class = repo["status"]
        ecosystems = ", ".join(repo["ecosystems"]) or "unknown"
        scan = repo.get("scan_result") or {}
        score = scan.get("score", "N/A")
        html_lines.append(
            f"<tr><td>{repo['repo_id']}</td><td>{ecosystems}</td>"
            f"<td class='{status_class}'>{repo['status']}</td><td>{score}</td></tr>"
        )

    html_lines.append("</table>")
    html_lines.append("<hr>")
    html_lines.append("<p><em>Generated by oss-paper-ci evaluation runner</em></p>")
    html_lines.append("</body></html>")

    return "\n".join(html_lines)


def compare_results(baseline: dict, current: dict) -> dict:
    """Compare two evaluation results."""
    comparison: dict[str, Any] = {
        "baseline_version": baseline.get("version"),
        "current_version": current.get("version"),
        "total_repos_baseline": baseline.get("total_repos", 0),
        "total_repos_current": current.get("total_repos", 0),
        "summary_diff": {},
        "repo_diffs": [],
    }

    # Compare summaries
    for key in ["pass", "partial", "fail", "evaluated", "error"]:
        b = baseline.get("summary", {}).get(key, 0)
        c = current.get("summary", {}).get(key, 0)
        comparison["summary_diff"][key] = {"baseline": b, "current": c, "delta": c - b}

    # Compare individual repos
    baseline_repos = {r["repo_id"]: r for r in baseline.get("repos", [])}
    current_repos = {r["repo_id"]: r for r in current.get("repos", [])}

    all_ids = sorted(set(list(baseline_repos.keys()) + list(current_repos.keys())))
    for repo_id in all_ids:
        b = baseline_repos.get(repo_id, {})
        c = current_repos.get(repo_id, {})

        diff: dict[str, Any] = {
            "repo_id": repo_id,
            "baseline_status": b.get("status", "missing"),
            "current_status": c.get("status", "missing"),
            "changed": b.get("status") != c.get("status"),
        }
        comparison["repo_diffs"].append(diff)

    return comparison


def format_compare_json(comparison: dict) -> str:
    """Format comparison results as JSON."""
    return json.dumps(comparison, indent=2, ensure_ascii=False)


def format_compare_markdown(comparison: dict) -> str:
    """Format comparison results as Markdown."""
    lines: list[str] = []
    lines.append("# Evaluation Comparison")
    lines.append("")
    lines.append(f"**Baseline Version:** {comparison['baseline_version']}")
    lines.append(f"**Current Version:** {comparison['current_version']}")
    lines.append(f"**Baseline Repos:** {comparison['total_repos_baseline']}")
    lines.append(f"**Current Repos:** {comparison['total_repos_current']}")
    lines.append("")

    lines.append("## Summary Diff")
    lines.append("")
    lines.append("| Metric | Baseline | Current | Delta |")
    lines.append("|--------|----------|---------|-------|")
    for key, val in comparison["summary_diff"].items():
        delta = val["delta"]
        sign = "+" if delta > 0 else ""
        lines.append(f"| {key} | {val['baseline']} | {val['current']} | {sign}{delta} |")
    lines.append("")

    # Repo diffs
    changed = [d for d in comparison["repo_diffs"] if d["changed"]]
    if changed:
        lines.append(f"## Changed Repos ({len(changed)})")
        lines.append("")
        lines.append("| Repo ID | Baseline | Current |")
        lines.append("|---------|----------|---------|")
        for d in changed:
            lines.append(f"| {d['repo_id']} | {d['baseline_status']} | {d['current_status']} |")
        lines.append("")
    else:
        lines.append("No repo status changes detected.")
        lines.append("")

    lines.append("---")
    lines.append("*Generated by oss-paper-ci evaluation runner*")

    return "\n".join(lines)
