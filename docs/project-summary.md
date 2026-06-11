# Project Summary

OSS-Paper-CI is a command-line toolkit for checking, attempting, packaging, and explaining reproducibility evidence for scientific code repositories.

## Motivation

Scientific papers increasingly depend on code, data, and computational environments. Reviewers, readers, and authors need practical ways to assess whether a repository can be reproduced. Manual reproduction is time-consuming and error-prone. Existing CI tools check syntax and tests but not reproducibility-specific concerns like environment files, data documentation, and execution evidence.

## What I built

OSS-Paper-CI provides a structured, automated approach to reproducibility evidence:

- **Readiness scanning** that scores repositories on environment, data, experiments, results, and metadata
- **Safe reproduction attempts** that run in dry-run mode by default, recording what would happen without executing code
- **Reproduction capsules** that package all evidence into verifiable, archivable archives with integrity checksums
- **Reproducibility dossiers** that generate human-readable summaries for authors, reviewers, and maintainers
- **Workspace batch scanning** for checking multiple projects from a single configuration
- **Multi-language ecosystem detection** for Python, R, Julia, MATLAB/Octave, Node, Rust, Java, C/C++, Snakemake, Nextflow, Make, and shell
- **Terminal workbench** that orchestrates multiple analysis steps with progress display

## Safety boundary

OSS-Paper-CI records and explains reproducibility evidence. It does not prove scientific correctness, judge paper quality, or predict acceptance likelihood. The `--execute` flag is required to run any code. Dangerous commands are blocked. Every operation has a configurable timeout.

## Why it matters

Reproducibility is a spectrum, not a binary. OSS-Paper-CI helps scientific communities move along that spectrum by making reproducibility evidence visible, structured, and actionable. A low score does not mean a paper is wrong — it means the repository could benefit from better documentation and packaging. The tool produces evidence that authors can use to improve their repos and reviewers can use to assess reproducibility readiness.
