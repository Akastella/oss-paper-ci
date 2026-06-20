# Dependency Inventory

The `oss-paper-ci trust inventory` command generates an SBOM-like dependency inventory.

## Usage

```bash
oss-paper-ci trust inventory .
oss-paper-ci trust inventory . --format json
oss-paper-ci trust inventory . --format markdown
oss-paper-ci trust inventory . --output inventory.json
```

## What It Includes

- **Project metadata**: Name, version, Python requirement, license
- **Runtime dependencies**: From `pyproject.toml` `[project.dependencies]`
- **Dev dependencies**: From `pyproject.toml` `[project.optional-dependencies.dev]`
- **Optional dependencies**: All optional dependency groups
- **Scripts/entry points**: From `[project.scripts]`
- **GitHub Actions**: Actions used in `.github/workflows/*.yml`
- **Docker base images**: From `Dockerfile` and `docker-compose*.yml`
- **Detected lockfiles**: `requirements.lock`, `poetry.lock`, etc.
- **Ecosystems detected**: python, github-actions, docker, node, rust, go, etc.

## Example Output

```json
{
  "schema_version": "0.1",
  "report_type": "oss-paper-ci-dependency-inventory",
  "project": {
    "name": "my-project",
    "version": "1.0.0",
    "python_requires": ">=3.10",
    "license": "MIT"
  },
  "dependencies": {
    "runtime": ["pyyaml>=6.0", "rich>=13.0"],
    "dev": ["pytest>=7.0"]
  },
  "ecosystems_detected": ["python", "github-actions"],
  "limitations": [
    "Lightweight local inventory; not an official SPDX or CycloneDX SBOM."
  ]
}
```

## What It Does NOT Do

- **Not an official SBOM**: Does not claim SPDX or CycloneDX compliance
- **No transitive dependencies**: Only lists declared dependencies
- **No lockfile resolution**: Does not resolve exact versions
- **No vulnerability checking**: Does not check for known vulnerabilities

## See Also

- [trust.md](trust.md) — Trust & supply-chain security overview
- [SECURITY.md](../SECURITY.md) — Threat model and security policy
