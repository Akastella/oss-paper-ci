# PR Comment Generation

The `comment` command generates Markdown text suitable for pasting into a
GitHub Pull Request comment.

## Usage

```bash
oss-paper-ci comment --input report.json
oss-paper-ci comment --input report.json --output pr-comment.md
oss-paper-ci comment --input report.json --max-findings 5
```

## What it generates

- Score and status summary
- Count of pass/warn/fail checks
- Top findings with recommendations
- Suitable for GitHub PR comments

## Options

| Option | Description |
|--------|-------------|
| `--input` | Path to scan JSON report (required) |
| `--output` | Write to file instead of stdout |
| `--kind` | Comment type: scan or baseline |
| `--max-findings` | Maximum findings to show (default: 10) |

## Important

The `comment` command only generates Markdown text. It does **not**:
- Call the GitHub API
- Automatically post comments
- Require any GitHub permissions

To automatically post comments in CI, combine with `actions/github-script` or
the existing `scripts/comment_pr.py` helper.

## Example workflow

```yaml
- name: Generate PR comment
  run: |
    oss-paper-ci scan . --format json --output report.json
    oss-paper-ci comment --input report.json --output pr-comment.md

- name: Post comment
  if: github.event_name == 'pull_request'
  uses: actions/github-script@v7
  with:
    script: |
      const fs = require('fs');
      const comment = fs.readFileSync('pr-comment.md', 'utf8');
      // ... post comment via GitHub API
```

## Limitations

- Only reads JSON input (not Markdown or SARIF)
- Does not validate the JSON schema
- Does not include full evidence details
