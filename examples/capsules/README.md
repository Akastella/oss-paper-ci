# Capsule Examples

This directory contains examples of reproduction capsule usage.

**Note:** Actual `.zip` capsule files are not committed to the repository.
They are generated at runtime and should be distributed via CI artifacts
or release assets.

## Generate a Capsule

```bash
# Dry-run capsule
oss-paper-ci reproduce examples/demo-reproduce-repo \
  --dry-run --capsule demo-dry-run.zip

# Execute capsule
oss-paper-ci reproduce examples/demo-reproduce-repo \
  --execute --install --capsule demo-execute.zip
```

## Verify a Capsule

```bash
oss-paper-ci capsule verify demo-execute.zip
```

## Inspect a Capsule

```bash
oss-paper-ci capsule inspect demo-execute.zip --format markdown
oss-paper-ci capsule inspect demo-execute.zip --format json
```

## Compare Capsules

```bash
oss-paper-ci capsule diff demo-dry-run.zip demo-execute.zip
```

## See Also

- [reproduction-capsules.md](../../docs/reproduction-capsules.md)
- [capsule-format.md](../../docs/capsule-format.md)
- [capsule-verify.md](../../docs/capsule-verify.md)
- [capsule-security.md](../../docs/capsule-security.md)
