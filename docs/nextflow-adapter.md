# Nextflow Adapter

The Nextflow adapter detects Nextflow workflow projects.

## Detection

Files detected:
- `main.nf`, `nextflow.config`
- `modules/**/*.nf`

## Planning

**Dry-run only.** The adapter generates a preview command:
- `nextflow run . -preview` (preview planned processes)

## Runtime

Requires: `nextflow`

Support level: **dry-run**

## Limitations

- Nextflow runtime must be installed separately
- Workflow may require significant resources
- Container/singularity support may be needed
- **Execution is not supported** — only detection and planning

## Safety

Nextflow workflows are not automatically executed. Explicit confirmation is required.
