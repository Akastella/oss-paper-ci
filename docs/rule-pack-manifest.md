# Rule Pack Manifest

The rule pack manifest is a YAML file that defines custom checks without
writing Python code.  Each rule specifies a type, parameters, and
severity.

## File Format

```yaml
version: 1
name: my-rules
description: >
  Description of what this rule pack checks.

checks:
  - id: RULE001
    name: Rule name
    severity: warning
    category: metadata
    type: file_exists
    path: README.md
    message: "README.md is missing."
    recommendation: "Add a README.md file."
```

## Fields

### Top-level

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `version` | int | Yes | Manifest version (currently 1) |
| `name` | string | No | Human-readable name |
| `description` | string | No | Description of the rule pack |
| `checks` | list | Yes | List of rule definitions |

### Rule Definition

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `id` | string | Yes | Unique rule ID (e.g., LAB001) |
| `name` | string | Yes | Human-readable name |
| `severity` | string | No | Severity level (default: warning) |
| `category` | string | No | Category (default: custom) |
| `type` | string | Yes | Rule type |
| `message` | string | No | Message shown on failure |
| `recommendation` | string | No | Recommendation text |
| (type-specific) | varies | — | Parameters for the rule type |

## Rule Types

### `file_exists`

Check that a specific file exists.

```yaml
type: file_exists
path: CITATION.cff
```

### `any_file_exists`

Check that at least one of several files exists.

```yaml
type: any_file_exists
paths:
  - requirements.txt
  - environment.yml
  - pyproject.toml
```

### `forbidden_path`

Fail if a specific path exists.

```yaml
type: forbidden_path
path: secrets.json
```

### `forbidden_glob`

Fail if any file matching a glob exists.

```yaml
type: forbidden_glob
pattern: "data/**/*.zip"
```

### `text_contains`

Check that a file contains specific text.

```yaml
type: text_contains
path: README.md
text: "## Installation"
```

### `regex_contains`

Check that a file matches a regular expression.

```yaml
type: regex_contains
path: README.md
pattern: "(?i)(cite|citation)"
```

### `yaml_key_exists`

Check that a YAML file has a specific key.  Supports dotted paths.

```yaml
type: yaml_key_exists
path: pyproject.toml
key: project.name
```

## Severity Levels

| Level | Internal | Effect |
|-------|----------|--------|
| `error` | error | Always fails the scan |
| `blocking` | error | Same as error |
| `warning` | warning | Affects score and status |
| `important` | warning | Same as warning |
| `info` | info | Informational only |
| `advisory` | info | Same as info |

## Validation

```bash
oss-paper-ci rules validate --rules my-rules.yml
```

This checks:
- YAML syntax
- Required fields
- Valid rule types
- Valid severity values
- Duplicate rule IDs
- Type-specific parameter requirements

## Examples

See [examples/rule-packs/](../examples/rule-packs/) for working examples.
