# Design Decisions

## Decision Log

### 1. Python version: 3.10+
Rationale: 3.10 is the oldest version still in active support. Provides match statements and union type syntax.

### 2. Minimal dependencies: only PyYAML
Rationale: YAML parsing is the one thing stdlib doesn't provide. All other functionality uses stdlib. This keeps installation simple and reduces supply chain risk.

### 3. argparse over typer/click
Rationale: stdlib CLI framework means zero additional dependencies. The CLI is simple enough that argparse is sufficient.

### 4. dataclasses over pydantic
Rationale: stdlib dataclasses have no dependency cost. The data models are simple enough that pydantic validation is unnecessary.

### 5. Registry pattern for checkers
Rationale: Each checker module uses @register decorator. New checks can be added by creating a new module with decorated classes. No need to edit a central registry file.

### 6. Scoring by category weights
Rationale: Different check categories have different importance for reproducibility. Environment (20) and Experiments (20) are weighted highest because they are most critical for actual reproduction.

### 7. Exit codes: 0=pass, 1=warn, 2=fail
Rationale: Standard CI convention. Allows GitHub Actions to distinguish between "needs attention" and "blocking failure".

### 8. No LLM dependency
Rationale: The tool must work offline, in CI, without API keys. All checks are deterministic rule-based checks. This is a feature, not a limitation.

### 9. JSON schema version field
Rationale: The report schema includes a version field to allow future evolution without breaking consumers.

### 10. Agent Teams structure
Rationale: 7 parallel checker agents + test-fixtures + documentation agents for maximum parallelism. Foundation (models, CLI, scanner) built first as contracts, then agents build modules independently.
