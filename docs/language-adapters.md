# Language Adapters

oss-paper-ci uses a language adapter framework to detect, plan, and report on reproduction steps across different programming language ecosystems.

## Supported Adapters

| Adapter | Language | Detect | Plan | Execute | Runtime |
|---------|----------|--------|------|---------|---------|
| python | Python | ✅ | ✅ | ✅ | python3 |
| r | R | ✅ | ✅ | ✅ | Rscript |
| julia | Julia | ✅ | ✅ | ✅ | julia |
| matlab | MATLAB/Octave | ✅ | ✅ | ❌ | matlab/octave |
| node | Node.js | ✅ | ✅ | ✅ | node |
| rust | Rust | ✅ | ✅ | ✅ | cargo |
| java | Java | ✅ | ✅ | ✅ | java |
| cpp | C/C++ | ✅ | ✅ | ✅ | g++ |
| make | Make | ✅ | ✅ | ✅ | make |
| snakemake | Snakemake | ✅ | ✅ | ❌ | snakemake |
| nextflow | Nextflow | ✅ | ✅ | ❌ | nextflow |
| shell | Shell Scripts | ✅ | ✅ | ✅ | bash |

## Usage

```bash
# List all adapters
oss-paper-ci adapters list

# Inspect a repository
oss-paper-ci adapters inspect /path/to/repo

# Generate a plan
oss-paper-ci adapters plan /path/to/repo

# Diagnose runtime availability
oss-paper-ci adapters doctor /path/to/repo
```

## Safety

- All adapters default to dry-run mode
- Missing runtimes are reported as unavailable, not as errors
- Shell scripts with dangerous commands are flagged
- No code is executed without explicit `--execute` flag
- No runtimes are automatically installed
