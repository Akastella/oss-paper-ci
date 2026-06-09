# Rule Pack Examples

This directory contains example rule pack manifests for oss-paper-ci.

## Available Rule Packs

| File | Description |
|------|-------------|
| `lab-reproducibility-rules.yml` | General reproducibility checks for lab papers |
| `citation-required.yml` | Checks for CITATION.cff and citation references |
| `no-large-data.yml` | Forbids large data files in the repository |

## Usage

### CLI

```bash
# Validate a rule pack
oss-paper-ci rules validate --rules examples/rule-packs/lab-reproducibility-rules.yml

# List rules in a pack
oss-paper-ci rules list --rules examples/rule-packs/lab-reproducibility-rules.yml

# Scan with a rule pack
oss-paper-ci scan . --rules examples/rule-packs/lab-reproducibility-rules.yml
```

### Config file

```yaml
# .oss-paper-ci.yml
version: 1
profile: default

rule_packs:
  - examples/rule-packs/lab-reproducibility-rules.yml
```

### GitHub Action

```yaml
- uses: Akastella/oss-paper-ci@v1
  with:
    rules: examples/rule-packs/lab-reproducibility-rules.yml
```

## Writing Your Own Rule Pack

See [docs/rule-pack-manifest.md](../../docs/rule-pack-manifest.md) for the
full manifest specification.

### Minimal Example

```yaml
version: 1
name: my-rules
description: Custom rules for my project.

checks:
  - id: MY001
    name: Require README
    severity: error
    category: metadata
    type: file_exists
    path: README.md
    message: "README.md is required."
```

### Supported Rule Types

| Type | Description | Required Params |
|------|-------------|-----------------|
| `file_exists` | Check that a file exists | `path` |
| `any_file_exists` | Check that at least one file exists | `paths` (list) |
| `forbidden_path` | Fail if a path exists | `path` |
| `forbidden_glob` | Fail if any matching file exists | `pattern` |
| `text_contains` | Check that a file contains text | `path`, `text` |
| `regex_contains` | Check that a file matches a regex | `path`, `pattern` |
| `yaml_key_exists` | Check that a YAML file has a key | `path`, `key` |

### Severity Levels

| Level | Description |
|-------|-------------|
| `error` / `blocking` | Always fails the scan |
| `warning` / `important` | Affects score and status |
| `info` / `advisory` | Informational only |
