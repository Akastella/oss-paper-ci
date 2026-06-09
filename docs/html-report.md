# HTML Report

oss-paper-ci can generate a static HTML report for easy viewing in a browser.

## Usage

```bash
oss-paper-ci scan . --format html --output report.html
```

## What it contains

- Score and status summary
- Blocking, important, and advisory findings
- Recommendations for failed checks
- Self-contained CSS (no external CDN)

## Characteristics

- Single-file HTML (no external dependencies)
- No JavaScript required
- Works offline
- Suitable for CI artifacts or sharing via email

## Limitations

- HTML report is a static snapshot, not an interactive dashboard
- No filtering or sorting capabilities
- No real-time updates

## Example

```bash
oss-paper-ci scan tests/fixtures/realistic_ml_repo --format html --output report.html
open report.html  # macOS
xdg-open report.html  # Linux
start report.html  # Windows
```

See [examples/reports/realistic_ml_report.html](../examples/reports/realistic_ml_report.html)
for a generated example.
