#!/usr/bin/env python3
"""Scale gate: verify batch scanning works correctly at small scale.

Runs batch scan with jobs=1 and jobs=2, verifies semantic equivalence,
and records runtime.
"""

from __future__ import annotations

import argparse
import json
import sys
import tempfile
import time
from pathlib import Path

# Add src to path for direct execution
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from oss_paper_ci.batch import run_batch_scan
from oss_paper_ci.workspace import load_workspace


def generate_mini_workspace(corpus_dir: Path, workspace_file: Path, count: int = 5) -> None:
    """Generate a temporary workspace file for the corpus."""
    projects = []
    for i in range(1, count + 1):
        repo_dir = corpus_dir / f"repo_{i:03d}"
        if repo_dir.exists():
            projects.append(f"""  - id: repo_{i:03d}
    path: {repo_dir}""")

    content = f"""version: 1
name: scale-gate-test
defaults:
  profile: default
projects:
{chr(10).join(projects)}
"""
    workspace_file.write_text(content, encoding="utf-8")


def run_scale_gate(corpus_dir: Path, repo_count: int = 5) -> dict:
    """Run the scale gate test.

    Returns:
        Dict with test results.
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        workspace_file = Path(tmpdir) / "scale-workspace.yml"
        generate_mini_workspace(corpus_dir, workspace_file, count=repo_count)

        workspace = load_workspace(workspace_file)

        # Run with jobs=1
        start_1 = time.monotonic()
        result_1 = run_batch_scan(workspace, workspace_file, jobs=1, use_cache=False)
        time_1 = time.monotonic() - start_1

        # Run with jobs=2
        start_2 = time.monotonic()
        result_2 = run_batch_scan(workspace, workspace_file, jobs=2, use_cache=False)
        time_2 = time.monotonic() - start_2

        # Compare semantics
        dict_1 = result_1.to_dict()
        dict_2 = result_2.to_dict()

        semantic_match = True
        mismatches = []

        # Compare project count
        if len(dict_1["projects"]) != len(dict_2["projects"]):
            semantic_match = False
            mismatches.append("project count differs")

        # Compare each project
        projects_1 = {p["id"]: p for p in dict_1["projects"]}
        projects_2 = {p["id"]: p for p in dict_2["projects"]}

        for pid in sorted(set(projects_1) | set(projects_2)):
            p1 = projects_1.get(pid)
            p2 = projects_2.get(pid)
            if p1 is None or p2 is None:
                semantic_match = False
                mismatches.append(f"project {pid} missing in one run")
                continue
            if p1.get("score") != p2.get("score"):
                semantic_match = False
                mismatches.append(f"{pid}: score {p1.get('score')} vs {p2.get('score')}")
            if p1.get("status") != p2.get("status"):
                semantic_match = False
                mismatches.append(f"{pid}: status {p1.get('status')} vs {p2.get('status')}")

        # Compare summary
        s1 = dict_1.get("summary", {})
        s2 = dict_2.get("summary", {})
        if s1.get("average_score") != s2.get("average_score"):
            semantic_match = False
            mismatches.append(f"average score {s1.get('average_score')} vs {s2.get('average_score')}")

        return {
            "corpus_dir": str(corpus_dir),
            "repo_count": repo_count,
            "jobs_1_runtime": round(time_1, 3),
            "jobs_2_runtime": round(time_2, 3),
            "semantic_match": semantic_match,
            "mismatches": mismatches,
            "pass": semantic_match,
            "summary_jobs_1": s1,
            "summary_jobs_2": s2,
        }


def format_markdown(result: dict) -> str:
    """Format scale gate result as Markdown."""
    lines = ["# Scale Gate Report\n"]

    lines.append("| Metric | Value |")
    lines.append("|--------|-------|")
    lines.append(f"| Corpus size | {result['repo_count']} |")
    lines.append(f"| Jobs 1 runtime | {result['jobs_1_runtime']:.1f}s |")
    lines.append(f"| Jobs 2 runtime | {result['jobs_2_runtime']:.1f}s |")
    lines.append(f"| Semantic match | {'yes' if result['semantic_match'] else 'no'} |")
    lines.append(f"| Pass | {'yes' if result['pass'] else 'no'} |")
    lines.append("")

    if result.get("mismatches"):
        lines.append("## Mismatches\n")
        for m in result["mismatches"]:
            lines.append(f"- {m}")
        lines.append("")

    lines.append("## Summary Comparison\n")
    lines.append("| Metric | Jobs 1 | Jobs 2 |")
    lines.append("|--------|--------|--------|")
    s1 = result.get("summary_jobs_1", {})
    s2 = result.get("summary_jobs_2", {})
    for key in ["pass", "warn", "fail", "error", "average_score"]:
        lines.append(f"| {key} | {s1.get(key, '-')} | {s2.get(key, '-')} |")
    lines.append("")

    lines.append("---")
    lines.append("*Scale gate is an engineering regression test, not an academic benchmark.*")
    lines.append("")

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="Run scale gate.")
    parser.add_argument("--corpus", default="tests/fixtures/synthetic_corpus",
                        help="Path to synthetic corpus directory.")
    parser.add_argument("--count", type=int, default=5,
                        help="Number of repos to use (must already exist).")
    parser.add_argument("--format", choices=["json", "markdown"], default="markdown")
    parser.add_argument("--output", "-o", help="Output file path.")
    args = parser.parse_args()

    corpus_dir = Path(args.corpus)
    if not corpus_dir.exists():
        print(f"Error: corpus directory not found: {corpus_dir}", file=sys.stderr)
        print("Run: python scripts/generate_synthetic_corpus.py --count 20 --output tests/fixtures/synthetic_corpus",
              file=sys.stderr)
        sys.exit(1)

    result = run_scale_gate(corpus_dir, repo_count=args.count)

    if args.format == "json":
        text = json.dumps(result, indent=2, ensure_ascii=False)
    else:
        text = format_markdown(result)

    if args.output:
        Path(args.output).write_text(text, encoding="utf-8")
        print(f"Report written to {args.output}")
    else:
        print(text)

    if not result["pass"]:
        print("\nScale gate FAILED", file=sys.stderr)
        sys.exit(1)
    else:
        print("\nScale gate PASSED")


if __name__ == "__main__":
    main()
