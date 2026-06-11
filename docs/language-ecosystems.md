# Language Ecosystems

OSS-Paper-CI can detect multiple research software ecosystems, but
support level varies by runtime availability.

## Supported Ecosystems

| Ecosystem | Support Level | Runtime Required |
|-----------|---------------|------------------|
| Python | native | python3 |
| R | execute-if-runtime-present | Rscript |
| Julia | execute-if-runtime-present | julia |
| MATLAB/Octave | dry-run / execute-if-runtime-present | matlab / octave |
| Node.js | execute-if-runtime-present | node |
| Rust | execute-if-runtime-present | cargo |
| Java | execute-if-runtime-present | java |
| C/C++ | execute-if-runtime-present | g++ |
| Make | execute-if-runtime-present | make |
| Snakemake | dry-run | snakemake |
| Nextflow | dry-run | nextflow |
| Shell | execute-if-runtime-present | bash |

## Support Levels

- **native**: Fully supported. Python is the primary ecosystem.
- **execute-if-runtime-present**: Can detect, plan, and execute if the runtime is installed.
- **dry-run**: Can detect and plan, but will not execute automatically.
- **detect-only**: Can only detect presence.

## Detect Ecosystems

```bash
# Detect all ecosystems in a repository
oss-paper-ci ecosystems detect /path/to/repo

# JSON output
oss-paper-ci ecosystems detect /path/to/repo --format json

# Explain a specific ecosystem
oss-paper-ci ecosystems explain r
oss-paper-ci ecosystems explain julia
oss-paper-ci ecosystems explain snakemake
```

## Reproduce with Ecosystem

```bash
# Dry-run reproduction targeting R
oss-paper-ci reproduce /path/to/repo --ecosystem r --dry-run

# Dry-run reproduction targeting Julia
oss-paper-ci reproduce /path/to/repo --ecosystem julia --dry-run

# Dry-run reproduction targeting Snakemake
oss-paper-ci reproduce /path/to/repo --ecosystem snakemake --dry-run
```

## Important Notes

- **Runtime not installed**: The tool will detect the ecosystem but report
  it as "runtime not available". It will not attempt to install the runtime.
- **Multiple ecosystems**: A repository may have multiple ecosystems detected.
  Use `--ecosystem` to select one for reproduction.
- **Not a guarantee**: Detection does not mean the project will run correctly.
  It means the tool recognized the ecosystem's files and patterns.
- **Safety first**: Only Python has native support. Other ecosystems require
  explicit `--execute` and a trusted repository.

## See Also

- [Reproduce](reproduce.md)
- [Security Model](security-model.md)
- [Failure Taxonomy](failure-taxonomy.md)
