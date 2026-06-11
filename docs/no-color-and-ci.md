# No-Color and CI Support

OSS-Paper-CI respects the `NO_COLOR` convention and automatically
detects CI environments.

## NO_COLOR Convention

Set `NO_COLOR=1` to disable all color output:

```bash
export NO_COLOR=1
oss-paper-ci workbench .
```

This follows the [no-color.org](https://no-color.org) standard.

## CI Auto-Detection

OSS-Paper-CI detects these CI environments automatically:

- GitHub Actions
- Travis CI
- CircleCI
- Jenkins
- GitLab CI
- Azure Pipelines
- Buildkite
- AWS CodeBuild
- Bitbucket Pipelines

In CI, color and animation are disabled by default.

## GitHub Actions Example

```yaml
- name: Run workbench
  run: oss-paper-ci workbench . --plain --output-dir results
  env:
    NO_COLOR: "1"
    OSS_PAPER_CI_NO_ANIMATE: "1"
```

## Environment Variables

| Variable | Values | Effect |
|----------|--------|--------|
| `NO_COLOR` | Any non-empty value | Disable color |
| `OSS_PAPER_CI_NO_COLOR` | `1`, `true`, `yes` | Disable color |
| `OSS_PAPER_CI_NO_ANIMATE` | `1`, `true`, `yes` | Disable animation |
| `OSS_PAPER_CI_PLAIN` | `1`, `true`, `yes` | Force plain mode |

## Priority

Command-line flags take precedence over environment variables:

1. `--plain` (highest priority)
2. `--no-color`
3. `NO_COLOR` / `OSS_PAPER_CI_NO_COLOR`
4. CI auto-detection
5. TTY detection

## Testing

In tests, use `--plain` or set `NO_COLOR=1` to get deterministic output:

```python
result = subprocess.run(
    ["oss-paper-ci", "wizard", "--plain", "."],
    capture_output=True, text=True,
)
assert "\x1b[" not in result.stdout  # No ANSI escapes
```
