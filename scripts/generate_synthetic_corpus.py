#!/usr/bin/env python3
"""Generate synthetic corpus for scale testing.

Creates small test repositories with deterministic content.
"""

from __future__ import annotations

import argparse
import os
from pathlib import Path


def generate_repo(repo_dir: Path, index: int) -> None:
    """Generate a single synthetic repository."""
    repo_dir.mkdir(parents=True, exist_ok=True)

    # README
    readme_content = f"""# Synthetic Repository {index:03d}

This is a synthetic repository for scale testing.

## Usage

```bash
python main.py
```

## License

MIT
"""
    (repo_dir / "README.md").write_text(readme_content, encoding="utf-8")

    # LICENSE
    license_content = """MIT License

Copyright (c) 2024 Synthetic Test

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""
    (repo_dir / "LICENSE").write_text(license_content, encoding="utf-8")

    # requirements.txt
    (repo_dir / "requirements.txt").write_text(
        f"numpy>=1.24.0\npandas>=2.0.0\n# Repo {index:03d}\n",
        encoding="utf-8",
    )

    # main.py
    main_content = f"""\"\"\"Synthetic repository {index:03d} main script.\"\"\"

import sys


def main():
    print(f"Hello from synthetic repo {index:03d}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
"""
    (repo_dir / "main.py").write_text(main_content, encoding="utf-8")

    # src directory
    src_dir = repo_dir / "src"
    src_dir.mkdir(exist_ok=True)
    (src_dir / "__init__.py").write_text("", encoding="utf-8")
    (src_dir / "model.py").write_text(
        f'"""Model for repo {index:03d}."""\n\nclass Model:\n    pass\n',
        encoding="utf-8",
    )

    # scripts directory
    scripts_dir = repo_dir / "scripts"
    scripts_dir.mkdir(exist_ok=True)
    (scripts_dir / "train.py").write_text(
        f'"""Training script for repo {index:03d}."""\n\nprint("Training...")\n',
        encoding="utf-8",
    )

    # results directory
    results_dir = repo_dir / "results"
    results_dir.mkdir(exist_ok=True)
    (results_dir / "metrics.json").write_text(
        f'{{"accuracy": 0.{index % 100:02d}, "repo": {index}}}\n',
        encoding="utf-8",
    )


def main():
    parser = argparse.ArgumentParser(description="Generate synthetic corpus.")
    parser.add_argument("--count", type=int, default=20, help="Number of repos to generate.")
    parser.add_argument("--output", required=True, help="Output directory.")
    parser.add_argument("--seed", type=int, default=42, help="Random seed (unused, for compatibility).")
    args = parser.parse_args()

    output_dir = Path(args.output)
    output_dir.mkdir(parents=True, exist_ok=True)

    for i in range(1, args.count + 1):
        repo_dir = output_dir / f"repo_{i:03d}"
        generate_repo(repo_dir, i)
        print(f"Generated {repo_dir}")

    print(f"\nGenerated {args.count} repos in {output_dir}")


if __name__ == "__main__":
    main()
