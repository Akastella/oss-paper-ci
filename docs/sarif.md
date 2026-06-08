# SARIF Output

oss-paper-ci supports SARIF (Static Analysis Results Interchange Format) v2.1.0
as an output format. SARIF is an OASIS standard for representing static analysis
results and is the format used by GitHub Code Scanning.

## Generating SARIF output

```bash
oss-paper-ci scan --format sarif -o results.sarif
```

The `--format sarif` flag produces a JSON file conforming to the SARIF v2.1.0
specification.

## What is SARIF

SARIF is a standardized JSON format for output from static analysis tools. It
defines a common structure for:

- **Tool information:** Name, version, and documentation URL.
- **Rules:** Each check becomes a SARIF rule with an ID, description, and
  default severity level.
- **Results:** Each check outcome becomes a SARIF result with a level
  (error, warning, note, none) and a message.

GitHub Code Scanning, VS Code, and other tools can ingest SARIF files to
display analysis results in a structured UI.

## Using with GitHub Code Scanning

### Upload SARIF in a workflow

```yaml
name: Reproducibility Scan

on:
  push:
    branches: [main]
  pull_request:

jobs:
  scan:
    runs-on: ubuntu-latest
    permissions:
      security-events: write
    steps:
      - uses: actions/checkout@v4

      - uses: actions/setup-python@v5
        with:
          python-version: "3.12"

      - run: pip install oss-paper-ci  # After PyPI publication

      - name: Generate SARIF report
        run: oss-paper-ci scan --format sarif -o results.sarif

      - name: Upload SARIF to GitHub
        uses: github/codeql-action/upload-sarif@v3
        with:
          sarif_file: results.sarif
```

After upload, results appear in the repository's **Security > Code scanning**
tab. Each check failure or warning shows as an alert with the check ID,
description, and recommendation.

### Severity mapping to SARIF levels

| Check status | SARIF level |
|-------------|-------------|
| fail        | error       |
| warn        | warning     |
| pass        | none        |
| unknown     | none        |

`none` means the result is informational and does not trigger an alert.

## Using with other tools

### VS Code SARIF Viewer

Install the [SARIF Viewer](https://marketplace.visualstudio.com/items?itemName=MS-SarifVSCode.sarif-viewer)
extension, then open the `.sarif` file. Results appear in the Problems panel.

### sarif-tools

The [sarif-tools](https://github.com/microsoft/sarif-tools) Python package
can summarize and filter SARIF output:

```bash
pip install sarif-tools
sarif summary results.sarif
```

### SARIF validation

Validate your SARIF file against the specification:

```bash
npm install -g @microsoft/sarif-multitool
sarif-multitool validate results.sarif
```

## SARIF schema structure

The generated SARIF file contains:

```json
{
  "$schema": "https://raw.githubusercontent.com/oasis-tcs/sarif-spec/main/sarif-2.1/schema/sarif-schema-2.1.0.json",
  "version": "2.1.0",
  "runs": [
    {
      "tool": {
        "driver": {
          "name": "oss-paper-ci",
          "version": "0.2.0",
          "informationUri": "https://github.com/Akastella/oss-paper-ci",
          "rules": [
            {
              "id": "META001",
              "name": "META001",
              "shortDescription": {"text": "README file exists"},
              "defaultConfiguration": {"level": "error"}
            }
          ]
        }
      },
      "results": [
        {
          "ruleId": "META001",
          "level": "none",
          "message": {"text": "Found README.md."},
          "relatedLocations": [
            {"id": 0, "message": {"text": "README.md"}}
          ]
        }
      ]
    }
  ]
}
```

### Key fields

| Field                  | Description                                          |
|------------------------|------------------------------------------------------|
| `runs[].tool.driver`   | Tool name, version, and link to documentation.       |
| `runs[].tool.driver.rules` | One entry per check, with ID and default level.  |
| `runs[].results`       | One entry per check outcome, with level and message. |
| `results[].level`      | `error`, `warning`, `note`, or `none`.               |
| `results[].message`    | Human-readable description including evidence.       |
| `results[].relatedLocations` | Evidence files or patterns as related locations. |
