# Workflow Audit

The `oss-paper-ci trust audit` command includes a GitHub Actions workflow audit.

## What It Checks

### Permissions

- **Missing permissions**: Warns when a workflow does not declare explicit `permissions:`
- **write-all**: Warns when a workflow uses `permissions: write-all`

### Triggers

- **pull_request_target**: High-risk trigger that can be exploited if it checks out PR code
- **workflow_run**: Medium-risk trigger

### Action Pinning

- **Official actions**: Accepts major version pinning (e.g., `actions/checkout@v4`)
- **Third-party actions**: Warns when not SHA-pinned
- **Unknown actions**: Warns when from an unrecognized source

### Known Official Actions

The following are recognized as official actions:
- `actions/checkout`
- `actions/setup-python`
- `actions/upload-artifact`
- `actions/download-artifact`
- `actions/cache`
- `github/codeql-action`
- And others in the built-in list

## Example Output

```
## Findings

### 1. Missing explicit permissions
- ID: workflow-missing-permissions
- Severity: medium
- Path: .github/workflows/ci.yml
- Message: Workflow does not declare explicit permissions.
- Recommendation: Add 'permissions: contents: read' or more specific permissions.

### 2. Third-party action: some-org/some-action@v1
- ID: workflow-third-party-action
- Severity: medium
- Path: .github/workflows/ci.yml
- Line: 15
- Recommendation: Pin third-party actions to SHA for supply-chain security.
```

## Limitations

- Static analysis of workflow YAML files only
- Does not verify action integrity or existence
- Does not check for secrets exposure in workflow logs
- Major version pinning (e.g., `@v4`) is accepted for official actions
- Does not verify if actions are compromised

## See Also

- [trust.md](trust.md) — Trust & supply-chain security overview
- [SECURITY.md](../SECURITY.md) — Threat model and security policy
