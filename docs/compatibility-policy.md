# Compatibility Policy

This document describes how oss-paper-ci maintains backward compatibility
across releases.

## Schema Versioning

The report JSON uses a `schema_version` field:

| Version | Introduced | Changes |
|---------|------------|---------|
| 0.1 | 0.1.0 | Initial format |
| 0.2 | 0.2.0 | Added metadata, score_breakdown, recommendations |
| 0.3 | 1.5.0rc1 | Added policy field |
| 0.4 | 1.6.0rc1 | Added suppressed_findings, rule_packs |

### Compatibility Rules

1. **New fields are additive**: Adding fields never breaks existing parsers.
2. **Existing fields are stable**: Field names and types don't change.
3. **Schema version bumps**: Only when the structure changes in a
   way that could affect parsers.
4. **Golden reports enforce stability**: Changes to scoring or checks
   require updating golden reports.

## CLI Compatibility

- **Commands are stable**: Existing commands don't change behavior.
- **New commands are additive**: New subcommands don't affect existing ones.
- **Flags are stable**: Existing flags don't change meaning.
- **New flags are optional**: New flags have sensible defaults.

## Config Compatibility

- **v0.1 configs still work**: Legacy configs are silently upgraded.
- **New fields are optional**: Missing fields use defaults.
- **Unknown keys warn**: Unknown config keys produce warnings, not errors.

## Check Compatibility

- **Check IDs are stable**: Existing check IDs don't change meaning.
- **New checks are additive**: New checks don't affect existing ones.
- **Severity can change**: But requires golden report update.
- **Custom checks are namespaced**: Rule pack IDs don't conflict with
  built-in checks.

## Breaking Changes

A breaking change is one that:

- Changes the meaning of an existing check ID
- Removes a CLI command or flag
- Changes the JSON report structure incompatibly
- Changes scoring weights without documentation

Breaking changes require:

1. A major version bump
2. Migration documentation
3. Golden report updates
4. Deprecation period (for commands/flags)

## Testing

Compatibility is enforced by:

- **Golden reports**: Snapshot tests for JSON output
- **Fixture matrix**: Expected scores for test fixtures
- **Schema validation**: Report structure validation
- **CI checks**: Automated tests on Python 3.10, 3.11, 3.12
