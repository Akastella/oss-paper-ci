#!/usr/bin/env python3
"""Update golden evaluation files from current evaluation results."""

import json
import sys
from pathlib import Path


def normalize_path(path_str: str) -> str:
    """Remove absolute paths, keep only relative."""
    # Replace common absolute path prefixes
    for prefix in ["C:\\", "/home/", "/Users/", "/tmp/"]:
        if prefix in path_str:
            idx = path_str.find(prefix)
            # Find the project root marker
            for marker in ["oss-paper-ci", "examples", "tests"]:
                marker_idx = path_str.find(marker, idx)
                if marker_idx != -1:
                    return path_str[marker_idx:]
    return path_str


def normalize_json(data: dict) -> dict:
    """Normalize JSON for golden file comparison."""
    # Remove timestamps if present
    if "timestamp" in data:
        del data["timestamp"]
    if "generated_at" in data:
        del data["generated_at"]

    # Normalize paths in string values
    json_str = json.dumps(data)
    json_str = normalize_path(json_str)

    return json.loads(json_str)


def update_golden_json(eval_json_path: Path, golden_path: Path):
    """Update golden JSON file."""
    with open(eval_json_path, "r") as f:
        data = json.load(f)

    # Normalize
    data = normalize_json(data)

    # Write golden file
    golden_path.parent.mkdir(parents=True, exist_ok=True)
    with open(golden_path, "w") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    print(f"Updated {golden_path}")


def update_golden_md(eval_md_path: Path, golden_path: Path):
    """Update golden Markdown file."""
    content = eval_md_path.read_text()

    # Normalize paths
    content = normalize_path(content)

    # Write golden file
    golden_path.parent.mkdir(parents=True, exist_ok=True)
    golden_path.write_text(content)

    print(f"Updated {golden_path}")


def main():
    project_root = Path(__file__).parent.parent
    eval_json = project_root / "examples" / "reports" / "evaluation_summary.json"
    eval_md = project_root / "examples" / "reports" / "evaluation_summary.md"
    golden_json = project_root / "tests" / "golden" / "evaluation_summary.json"
    golden_md = project_root / "tests" / "golden" / "evaluation_matrix.md"

    # Check if evaluation results exist
    if not eval_json.exists():
        print(f"Error: {eval_json} not found")
        print("Run: oss-paper-ci eval run examples/evaluation-corpus --format json --output examples/reports/evaluation_summary.json")
        sys.exit(1)

    if not eval_md.exists():
        print(f"Error: {eval_md} not found")
        print("Run: oss-paper-ci eval run examples/evaluation-corpus --format markdown --output examples/reports/evaluation_summary.md")
        sys.exit(1)

    # Update golden files
    update_golden_json(eval_json, golden_json)
    update_golden_md(eval_md, golden_md)

    print("\nGolden files updated successfully!")
    print("Run tests to verify: python -m pytest tests/test_evaluation_golden.py -v")


if __name__ == "__main__":
    main()
