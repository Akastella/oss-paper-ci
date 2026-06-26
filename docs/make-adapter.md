# Make Adapter

The Make adapter detects Makefile-based projects and generates reproduction plans.

## Detection

Files detected:
- `Makefile`, `makefile`, `GNUmakefile`

## Planning

Targets are parsed from the Makefile. Preferred targets (in order):
1. `reproduce`
2. `all`
3. `test`
4. `figures`
5. `tables`
6. `paper`

If no preferred target is found, the default target is used.

## Runtime

Requires: `make`

Support level: **execute-if-runtime-present**

## Limitations

- Make targets vary by project
- Default target may not be the reproduction target
