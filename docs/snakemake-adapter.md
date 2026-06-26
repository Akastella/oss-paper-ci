# Snakemake Adapter

The Snakemake adapter detects Snakemake workflow projects.

## Detection

Files detected:
- `Snakefile`, `workflow/Snakefile`
- `*.smk`, `workflow/rules/*.smk`
- `config.yaml`, `config.yml`

## Planning

**Dry-run only.** The adapter generates a preview command:
- `snakemake -n` (dry-run: show planned jobs)

## Runtime

Requires: `snakemake`

Support level: **dry-run**

## Limitations

- Snakemake runtime must be installed separately
- Workflow execution may require significant resources
- Data dependencies may not be available
- **Execution is not supported** — only detection and planning

## Safety

Snakemake workflows are not automatically executed. The `--cores` flag is required for execution, which is not provided by default.
