# Rule SDK

The Rule SDK allows you to extend oss-paper-ci with custom checks using
manifest-based rule packs.  No Python code is required.

## Quick Start

1. Create a rule pack YAML file:

```yaml
version: 1
name: my-rules
checks:
  - id: MY001
    name: Require README
    severity: error
    type: file_exists
    path: README.md
    message: "README.md is required."
```

2. Validate it:

```bash
oss-paper-ci rules validate --rules my-rules.yml
```

3. Use it in a scan:

```bash
oss-paper-ci scan . --rules my-rules.yml
```

4. Or add it to your config:

```yaml
# .oss-paper-ci.yml
rule_packs:
  - my-rules.yml
```

## Architecture

```
┌─────────────────┐     ┌──────────────────┐
│  Rule Pack YAML  │────▶│  Manifest Parser  │
└─────────────────┘     └──────────────────┘
                                │
                                ▼
                        ┌──────────────────┐
                        │  Rule Evaluators  │
                        │  (safe, static)   │
                        └──────────────────┘
                                │
                                ▼
                        ┌──────────────────┐
                        │   CheckResult[]   │
                        └──────────────────┘
                                │
                                ▼
                        ┌──────────────────┐
                        │  Scanner/Report   │
                        └──────────────────┘
```

## Safety

- **No code execution**: Rule packs are declarative YAML.  No Python
  or shell commands are executed.
- **Isolated evaluation**: Each rule is evaluated independently.  A
  failing rule does not crash the scan.
- **No network access**: Rules only access the local filesystem.
- **No side effects**: Rules produce CheckResult objects only.

## Rule Types

| Type | Description |
|------|-------------|
| `file_exists` | Check that a file exists |
| `any_file_exists` | Check that at least one of several files exists |
| `forbidden_path` | Fail if a path exists |
| `forbidden_glob` | Fail if any matching file exists |
| `text_contains` | Check that a file contains text |
| `regex_contains` | Check that a file matches a regex |
| `yaml_key_exists` | Check that a YAML file has a key |

See [rule-pack-manifest.md](rule-pack-manifest.md) for the full specification.

## Integration

### Policy Profiles

Custom rules work with policy profiles:

```bash
oss-paper-ci scan . --rules my-rules.yml --profile strict
```

### Disabled Checks

Custom rules can be disabled in config:

```yaml
checks:
  disabled:
    - MY001
```

### Severity Overrides

Custom rule severity can be overridden:

```yaml
checks:
  severity_overrides:
    MY001: info
```

### Suppressions

Custom rules can be suppressed:

```yaml
suppressions:
  findings:
    - id: MY001
      reason: "Not applicable to this project"
```

## Python API

For advanced use, the SDK exposes a Python API:

```python
from oss_paper_ci.checks.sdk import load_rule_pack, evaluate_rules

manifest = load_rule_pack("my-rules.yml")
results = evaluate_rules(manifest, "/path/to/repo")

for result in results:
    print(f"{result.id}: {result.status.value}")
```

## Limitations

- **Static checks only**: Rules can only check file existence, content,
  and structure.  They cannot execute code or make network requests.
- **No custom logic**: Complex validation requires writing a Python
  checker (see [check-authoring.md](check-authoring.md)).
- **No aggregation**: Each rule produces exactly one CheckResult.
  Cross-rule logic is not supported.

## Future Work

- Plugin-based custom checkers with sandboxed Python execution
- Rule composition and inheritance
- Cross-rule aggregation and conditional logic
- Remote rule pack discovery
