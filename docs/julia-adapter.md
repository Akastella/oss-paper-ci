# Julia Adapter

The Julia adapter detects Julia projects and generates reproduction plans.

## Detection

Files detected:
- `Project.toml`, `Manifest.toml`
- `*.jl`, `main.jl`, `run.jl`, `reproduce.jl`, `scripts/*.jl`

## Planning

Install steps:
- `Project.toml` → `julia --project -e 'using Pkg; Pkg.instantiate()'`

Run steps:
- `julia --project <script>` for Julia scripts

## Runtime

Requires: `julia`

Support level: **execute-if-runtime-present**

## Limitations

- Julia runtime must be installed separately
- Package installation may take significant time
- Some Julia packages may require system libraries
