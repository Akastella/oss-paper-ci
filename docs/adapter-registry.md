# Adapter Registry

The adapter registry is the central system for language detection and reproduction planning in oss-paper-ci.

## Architecture

```
AdapterRegistry
├── PythonAdapter
├── RAdapter
├── JuliaAdapter
├── MatlabAdapter
├── NodeAdapter
├── RustAdapter
├── JavaAdapter
├── CppAdapter
├── MakeAdapter
├── SnakemakeAdapter
├── NextflowAdapter
└── ShellAdapter
```

## How It Works

1. **Detection**: Each adapter scans a repository for language-specific files
2. **Planning**: Adapters generate install and run steps based on detected files
3. **Safety**: Adapters define safety rules for dangerous command blocking
4. **Runtime**: Adapters check if required runtimes are available

## CLI Commands

| Command | Description |
|---------|-------------|
| `adapters list` | List all registered adapters |
| `adapters inspect PATH` | Detect adapters for a repository |
| `adapters explain LANG` | Show adapter details |
| `adapters plan PATH` | Generate reproduction plan |
| `adapters validate PATH` | Validate detection report |
| `adapters doctor PATH` | Diagnose runtime availability |

## Output Formats

All commands support:
- `--format json` — Machine-readable JSON
- `--format markdown` — Human-readable Markdown
- `--output FILE` — Write to file instead of stdout

## Integration

The adapter registry is used by:
- `ecosystems.py` — Language ecosystem detection
- `evidence.py` — Evidence report ecosystem section
- `reproduce.py` — Reproduction planning
- `trust.py` — Trust and security scanning

## Extending

To add a new language adapter:

1. Create `src/oss_paper_ci/adapters/newlang.py`
2. Subclass `AdapterBase`
3. Implement `detect()` and `plan()`
4. Register in `registry.py` `_register_all()`
5. Add tests in `tests/test_adapter_newlang.py`

See [adapter-schema.md](adapter-schema.md) for the report format.
