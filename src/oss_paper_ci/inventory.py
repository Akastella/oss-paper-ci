"""Dependency inventory (SBOM-like) module."""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


@dataclass
class DependencyInventory:
    """Lightweight dependency inventory."""

    schema_version: str = "0.1"
    report_type: str = "oss-paper-ci-dependency-inventory"
    repo: str = "."
    project_name: str = ""
    project_version: str = ""
    python_requires: str = ""
    runtime_dependencies: list[str] = field(default_factory=list)
    optional_dependencies: dict[str, list[str]] = field(default_factory=dict)
    dev_dependencies: list[str] = field(default_factory=list)
    scripts: dict[str, str] = field(default_factory=dict)
    lockfiles_detected: list[str] = field(default_factory=list)
    github_actions_used: list[dict[str, str]] = field(default_factory=list)
    docker_base_images: list[str] = field(default_factory=list)
    ecosystems_detected: list[str] = field(default_factory=list)
    license: str = ""
    project_urls: dict[str, str] = field(default_factory=dict)
    limitations: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema_version": self.schema_version,
            "report_type": self.report_type,
            "repo": self.repo,
            "project": {
                "name": self.project_name,
                "version": self.project_version,
                "python_requires": self.python_requires,
                "license": self.license,
                "urls": self.project_urls,
            },
            "dependencies": {
                "runtime": self.runtime_dependencies,
                "optional": self.optional_dependencies,
                "dev": self.dev_dependencies,
            },
            "scripts": self.scripts,
            "lockfiles_detected": self.lockfiles_detected,
            "github_actions_used": self.github_actions_used,
            "docker_base_images": self.docker_base_images,
            "ecosystems_detected": self.ecosystems_detected,
            "limitations": self.limitations,
        }


def _parse_pyproject_toml(path: Path) -> dict[str, Any]:
    """Parse pyproject.toml using stdlib only (tomllib in 3.11+)."""
    try:
        import tomllib
    except ImportError:
        # Fallback for 3.10
        try:
            import tomli as tomllib  # type: ignore[no-redef]
        except ImportError:
            # Minimal parser fallback
            return _parse_pyproject_minimal(path)

    with open(path, "rb") as f:
        return tomllib.load(f)


def _parse_pyproject_minimal(path: Path) -> dict[str, Any]:
    """Minimal fallback parser for pyproject.toml."""
    content = path.read_text(encoding="utf-8")
    result: dict[str, Any] = {"project": {}, "tool": {}}

    # Extract project name
    m = re.search(r'name\s*=\s*"([^"]+)"', content)
    if m:
        result["project"]["name"] = m.group(1)

    # Extract version
    m = re.search(r'version\s*=\s*"([^"]+)"', content)
    if m:
        result["project"]["version"] = m.group(1)

    # Extract python requires
    m = re.search(r'requires-python\s*=\s*"([^"]+)"', content)
    if m:
        result["project"]["requires-python"] = m.group(1)

    # Extract dependencies (simple list)
    deps = []
    in_deps = False
    for line in content.splitlines():
        if "dependencies" in line and "=" in line:
            in_deps = True
            # Check for inline deps
            m = re.search(r'dependencies\s*=\s*\[(.+)\]', line)
            if m:
                for dep in re.findall(r'"([^"]+)"', m.group(1)):
                    deps.append(dep)
                in_deps = False
            continue
        if in_deps:
            m = re.match(r'\s*"([^"]+)"', line)
            if m:
                deps.append(m.group(1))
            elif line.strip().startswith("]"):
                in_deps = False

    if deps:
        result["project"]["dependencies"] = deps

    return result


def build_inventory(repo_path: str | Path) -> DependencyInventory:
    """Build a dependency inventory for the repository."""
    root = Path(repo_path).resolve()
    inv = DependencyInventory(
        repo=str(root),
        limitations=[
            "Lightweight local inventory; not an official SPDX or CycloneDX SBOM.",
            "Based on declared metadata, not resolved dependency tree.",
            "Does not include transitive dependencies.",
            "GitHub Actions versions are as declared in workflow files.",
        ]
    )

    # Parse pyproject.toml
    pyproject_path = root / "pyproject.toml"
    if pyproject_path.exists():
        inv.ecosystems_detected.append("python")
        data = _parse_pyproject_toml(pyproject_path)
        project = data.get("project", {})
        inv.project_name = project.get("name", "")
        inv.project_version = project.get("version", "")
        inv.python_requires = project.get("requires-python", "")

        # Dependencies
        deps = project.get("dependencies", [])
        inv.runtime_dependencies = list(deps) if isinstance(deps, list) else []

        # Optional dependencies
        opt_deps = project.get("optional-dependencies", {})
        if isinstance(opt_deps, dict):
            inv.optional_dependencies = {k: list(v) for k, v in opt_deps.items()}
            inv.dev_dependencies = list(opt_deps.get("dev", []))

        # Scripts
        scripts = project.get("scripts", {})
        if isinstance(scripts, dict):
            inv.scripts = dict(scripts)

        # License
        license_info = project.get("license", {})
        if isinstance(license_info, dict):
            inv.license = license_info.get("text", "")
        elif isinstance(license_info, str):
            inv.license = license_info

        # URLs
        urls = project.get("urls", {})
        if isinstance(urls, dict):
            inv.project_urls = dict(urls)

    # Detect lockfiles
    lockfile_names = [
        "requirements.txt", "requirements.lock", "poetry.lock",
        "Pipfile.lock", "pdm.lock", "uv.lock", "conda-lock.yml",
    ]
    for lf in lockfile_names:
        if (root / lf).exists():
            inv.lockfiles_detected.append(lf)

    # Scan GitHub Actions workflows
    workflows_dir = root / ".github" / "workflows"
    if workflows_dir.exists():
        inv.ecosystems_detected.append("github-actions")
        for wf_file in workflows_dir.glob("*.yml"):
            try:
                content = wf_file.read_text(encoding="utf-8", errors="ignore")
                # Find 'uses:' directives
                for match in re.finditer(r"uses:\s*([^\s#]+)", content):
                    action = match.group(1)
                    if action and not action.startswith("./"):
                        inv.github_actions_used.append({
                            "action": action,
                            "workflow": wf_file.name,
                        })
            except Exception:
                continue

    # Scan Dockerfiles
    dockerfiles = list(root.glob("Dockerfile*")) + list(root.glob("docker-compose*.yml"))
    if dockerfiles:
        inv.ecosystems_detected.append("docker")
        for df in dockerfiles:
            try:
                content = df.read_text(encoding="utf-8", errors="ignore")
                for match in re.finditer(r"FROM\s+([^\s]+)", content):
                    img = match.group(1)
                    if img and img.lower() != "scratch":
                        inv.docker_base_images.append(img)
            except Exception:
                continue

    # Detect other ecosystems
    if (root / "package.json").exists():
        inv.ecosystems_detected.append("node")
    if (root / "Cargo.toml").exists():
        inv.ecosystems_detected.append("rust")
    if (root / "go.mod").exists():
        inv.ecosystems_detected.append("go")
    if (root / "Gemfile").exists():
        inv.ecosystems_detected.append("ruby")
    if (root / "pom.xml").exists() or (root / "build.gradle").exists():
        inv.ecosystems_detected.append("java")

    return inv


def format_inventory_markdown(inv: DependencyInventory) -> str:
    """Format inventory as Markdown."""
    lines = [
        "# Dependency Inventory",
        "",
        f"**Project:** {inv.project_name} v{inv.project_version}",
        f"**Python:** {inv.python_requires}",
        f"**License:** {inv.license or 'Not specified'}",
        "",
        "## Ecosystems Detected",
        "",
    ]

    for eco in inv.ecosystems_detected:
        lines.append(f"- {eco}")
    lines.append("")

    if inv.runtime_dependencies:
        lines.append("## Runtime Dependencies")
        lines.append("")
        for dep in inv.runtime_dependencies:
            lines.append(f"- `{dep}`")
        lines.append("")

    if inv.dev_dependencies:
        lines.append("## Dev Dependencies")
        lines.append("")
        for dep in inv.dev_dependencies:
            lines.append(f"- `{dep}`")
        lines.append("")

    if inv.optional_dependencies:
        lines.append("## Optional Dependencies")
        lines.append("")
        for group, deps in inv.optional_dependencies.items():
            lines.append(f"### {group}")
            for dep in deps:
                lines.append(f"- `{dep}`")
            lines.append("")

    if inv.scripts:
        lines.append("## Scripts / Entry Points")
        lines.append("")
        for name, cmd in inv.scripts.items():
            lines.append(f"- `{name}` → `{cmd}`")
        lines.append("")

    if inv.github_actions_used:
        lines.append("## GitHub Actions Used")
        lines.append("")
        for action in inv.github_actions_used:
            lines.append(f"- `{action['action']}` (in {action['workflow']})")
        lines.append("")

    if inv.docker_base_images:
        lines.append("## Docker Base Images")
        lines.append("")
        for img in inv.docker_base_images:
            lines.append(f"- `{img}`")
        lines.append("")

    if inv.lockfiles_detected:
        lines.append("## Lockfiles Detected")
        lines.append("")
        for lf in inv.lockfiles_detected:
            lines.append(f"- `{lf}`")
        lines.append("")

    lines.append("## Limitations")
    lines.append("")
    for lim in inv.limitations:
        lines.append(f"- {lim}")
    lines.append("")

    return "\n".join(lines)
