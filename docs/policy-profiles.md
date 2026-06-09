# Policy Profiles

Policy profiles are named parameter bundles that control how strictly
oss-paper-ci evaluates your repository.  Instead of tuning individual
config knobs, you pick a profile that matches your project's stage.

## Available Profiles

### `lenient`

Early-stage projects.  Fewer blocking findings; more items are advisory-only.
Useful when you want feedback without hard failures.

- **pass_score:** 70
- **warn_score:** 50
- **fail_under:** 30
- Citation, quickstart, contributing, pinned deps, data description,
  results directory, and CI checks are demoted to advisory.

### `default`

Balanced defaults.  Equivalent to pre-v1.5 behavior when no profile
is specified.  Suitable for most projects.

- **pass_score:** 85
- **warn_score:** 60
- **fail_under:** 50

### `strict`

Stricter governance.  Missing LICENSE, environment spec, data description,
and reproducibility script are all blocking.

- **pass_score:** 90
- **warn_score:** 70
- **fail_under:** 50
- LICENSE (META002), environment (ENV001), and data description (DATA001)
  are treated as blocking.

### `publication`

Publication-ready repos.  Requires LICENSE, environment, data description,
results directory, experiment description, and reproduction script.
Does **not** judge paper quality, correctness, or novelty.

- **pass_score:** 90
- **warn_score:** 75
- **fail_under:** 50
- LICENSE, environment, data description, and experiment description
  are treated as blocking.

## Using Profiles

### CLI

```bash
# Use a specific profile for a scan
oss-paper-ci scan . --profile strict

# Override profile from CLI (takes priority over config file)
oss-paper-ci scan . --profile publication --format json --output report.json
```

### Config file

```yaml
# .oss-paper-ci.yml
version: 1
profile: strict
```

### GitHub Action

```yaml
- uses: Akastella/oss-paper-ci@v1
  with:
    profile: publication
```

### Priority order

1. CLI `--profile` flag (highest priority)
2. Config file `profile` field
3. Default (`default`)

## Explaining a Profile

```bash
oss-paper-ci explain policy strict
```

This prints the profile's thresholds, check overrides, and blocking rules.

## Customizing a Profile

Profiles set defaults, but you can still override individual checks in
your config file:

```yaml
version: 1
profile: strict

checks:
  severity_overrides:
    META005: info  # demote contributing check even under strict
```

Config file overrides take priority over profile defaults for individual
checks.
