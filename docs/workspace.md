# Workspace Configuration

A workspace defines multiple projects to scan in a single batch run.
This is a local batch scanning tool for managing multiple repositories,
not a cloud project management system.

## Workspace File Format

Create `oss-paper-ci-workspace.yml`:

```yaml
version: 1
name: my-workspace
defaults:
  profile: default
  config: ""
  rules: []
  fail_under: 0
projects:
  - id: project-a
    path: ./project-a
    profile: publication
  - id: project-b
    path: ./project-b
    profile: strict
  - id: project-c
    path: ./project-c
    allow_failure: true
```

## Fields

### Top-level

| Field | Required | Description |
|-------|----------|-------------|
| `version` | Yes | Must be `1` |
| `name` | No | Human-readable workspace name |
| `defaults` | No | Default values applied to all projects |
| `projects` | Yes | List of project entries |

### defaults

| Field | Default | Description |
|-------|---------|-------------|
| `profile` | `default` | Default policy profile |
| `config` | `""` | Default config file path |
| `rules` | `[]` | Default rule pack paths |
| `fail_under` | `0` | Default score threshold |

### projects[]

| Field | Required | Description |
|-------|----------|-------------|
| `id` | Yes | Unique project identifier |
| `path` | Yes | Path relative to workspace file |
| `profile` | No | Override policy profile |
| `config` | No | Override config file path |
| `rules` | No | Override rule pack paths |
| `fail_under` | No | Override score threshold |
| `allow_failure` | No | If true, project failure does not fail the batch |

## Validation

```bash
oss-paper-ci workspace validate --workspace oss-paper-ci-workspace.yml
```

Validation checks:
- Version is 1
- Projects list is non-empty
- All project IDs are unique
- All project paths are present
- Field types are correct

## Listing Projects

```bash
oss-paper-ci workspace list --workspace oss-paper-ci-workspace.yml
oss-paper-ci workspace list --workspace oss-paper-ci-workspace.yml --format json
```

## Path Resolution

Project paths are resolved relative to the directory containing the workspace file.
Absolute paths are also supported but reduce portability.

## Compatibility

- Workspace does not execute user scripts
- Workspace does not make network requests
- Workspace does not modify project files
