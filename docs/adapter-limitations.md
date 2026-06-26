# Adapter Limitations

This document describes the known limitations of the language adapter system.

## General Limitations

- **No cloud sandbox**: All execution happens locally, not in isolated cloud environments
- **No GPU orchestration**: GPU resource management is not supported
- **No automatic paper scoring**: The tool does not judge paper quality or predict acceptance
- **No scientific correctness verification**: The tool checks engineering completeness, not scientific validity
- **No automatic code repair**: The tool identifies issues but does not fix them

## Per-Language Support Depth

| Language | Detect | Plan | Execute | Notes |
|----------|--------|------|---------|-------|
| Python | ✅ | ✅ | ✅ | Native support, most complete |
| R | ✅ | ✅ | ⚠️ | Requires Rscript runtime |
| Julia | ✅ | ✅ | ⚠️ | Requires julia runtime |
| Node.js | ✅ | ✅ | ⚠️ | Requires node runtime |
| Rust | ✅ | ✅ | ⚠️ | Requires cargo toolchain |
| Java | ✅ | ✅ | ⚠️ | Requires java + Maven/Gradle |
| C/C++ | ✅ | ✅ | ⚠️ | Requires compiler toolchain |
| Make | ✅ | ✅ | ⚠️ | Requires make |
| Shell | ✅ | ✅ | ⚠️ | Requires bash, dangerous cmd blocking |
| MATLAB | ✅ | ✅ | ❌ | Dry-run only, requires license |
| Snakemake | ✅ | ✅ | ❌ | Dry-run only |
| Nextflow | ✅ | ✅ | ❌ | Dry-run only |

Legend: ✅ Full support, ⚠️ Requires runtime, ❌ Not supported

## Detection Limitations

- Detection is based on file presence, not content analysis
- Multiple languages in one repo may produce overlapping detections
- Confidence scores are relative, not absolute probabilities
- Some file patterns may match unrelated files

## Planning Limitations

- Plans are generated from file patterns, not project analysis
- Install steps assume standard package managers
- Run steps use common entrypoint patterns
- Complex build systems may not be fully represented

## Execution Limitations

- All execution is local (no containerization)
- No network isolation
- No resource limits beyond timeout
- Working directory is not fully sandboxed

## Runtime Detection

- Runtime detection uses `shutil.which()` which checks PATH
- Version detection is best-effort
- Some runtimes may require additional setup beyond detection

## See Also

- [adapter-safety.md](adapter-safety.md) — Safety boundaries
- [adapter-schema.md](adapter-schema.md) — Report format
- [limitations.md](limitations.md) — General tool limitations
