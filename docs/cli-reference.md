# CLI Reference

Auto-generated from `oss-paper-ci --help` output.

## Main

```
usage: oss-paper-ci [-h] [--version]
                    {scan,init,explain,list-checks,config,diff,rules,validate-contract,graph,workspace,batch,cache,reproduce,capsule,version,baseline,smoke,doctor,comment}
                    ...

Check reproducibility readiness of scientific paper repositories.

positional arguments:
  {scan,init,explain,list-checks,config,diff,rules,validate-contract,graph,workspace,batch,cache,reproduce,capsule,version,baseline,smoke,doctor,comment}
    scan                Scan a repository for reproducibility checks.
    init                Generate a default config or contract file.
    explain             Explain a check ID or policy profile.
    list-checks         List all available checks.
    config              Configuration management.
    diff                Compare two scan reports.
    rules               Rule pack management.
    validate-contract   Validate a reproducibility contract.
    graph               Build and display evidence graph.
    workspace           Workspace management.
    batch               Batch scanning.
    cache               Cache management.
    reproduce           Attempt to reproduce a paper repository.
    capsule             Capsule management.
    version             Print version.
    baseline            Baseline management.
    smoke               Run smoke tests safely.
    doctor              Diagnose repository and environment.
    comment             Generate PR comment from scan results.

options:
  -h, --help            show this help message and exit
  --version             show program's version number and exit
```

## `oss-paper-ci scan`

Scan a repository for reproducibility readiness.

```
usage: oss-paper-ci scan [-h] [--config CONFIG_PATH] [--profile PROFILE]
                         [--format {json,markdown,sarif,html,github}]
                         [--output OUTPUT] [--fail-under FAIL_UNDER]
                         [--strict] [--verbose]
                         [--github-step-summary GITHUB_STEP_SUMMARY]
                         [--max-annotations MAX_ANNOTATIONS]
                         [--fail-on FAIL_ON] [--rules RULES_PATH]
                         [path]

positional arguments:
  path                  Path to repository root (default: .)

options:
  -h, --help            show this help message and exit
  --config CONFIG_PATH  Path to oss-paper-ci.yml config file.
  --profile PROFILE     Policy profile: lenient, default, strict, publication.
  --format {json,markdown,sarif,html,github}
                        Output format.
  --output OUTPUT, -o OUTPUT
                        Write report to file instead of stdout.
  --fail-under FAIL_UNDER
                        Exit with code 1 if score is below this threshold.
  --strict              Exit with code 1 if any warnings exist.
  --verbose             Show all check details with evidence in markdown
                        report.
  --github-step-summary GITHUB_STEP_SUMMARY
                        Write Markdown summary to file (for
                        $GITHUB_STEP_SUMMARY).
  --max-annotations MAX_ANNOTATIONS
                        Max annotations for github format (default: 50).
  --fail-on FAIL_ON     Fail on severity level (e.g., major, error).
  --rules RULES_PATH    Path to rule pack manifest YAML.
```

## `oss-paper-ci reproduce`

Attempt to reproduce a paper repository.

```
usage: oss-paper-ci reproduce [-h] [--repo REPO_OVERRIDE] [--dry-run]
                              [--execute] [--install] [--no-install]
                              [--command REPRODUCE_COMMAND]
                              [--workdir WORKDIR] [--keep-workdir]
                              [--timeout TIMEOUT]
                              [--format {markdown,json,html}]
                              [--output OUTPUT] [--capsule CAPSULE_PATH]
                              [--capsule-include-artifacts]
                              [--capsule-max-artifact-mb CAPSULE_MAX_ARTIFACT_MB]
                              url

positional arguments:
  url                   GitHub URL, local path, or paper URL.

options:
  -h, --help            show this help message and exit
  --repo REPO_OVERRIDE  Explicit repository URL (for paper URLs).
  --dry-run             Show what would happen without executing (default).
  --execute             Actually run commands (required for execution).
  --install             Install dependencies into isolated venv.
  --no-install          Skip dependency installation.
  --command REPRODUCE_COMMAND
                        Override the reproduction command.
  --workdir WORKDIR     Use a specific working directory.
  --keep-workdir        Preserve working directory after run.
  --timeout TIMEOUT     Per-command timeout in seconds (default: 300).
  --format {markdown,json,html}
                        Output format (default: markdown).
  --output OUTPUT, -o OUTPUT
                        Write report to file instead of stdout.
  --capsule CAPSULE_PATH
                        Generate a reproduction capsule zip at this path.
  --capsule-include-artifacts
                        Include generated artifacts in capsule.
  --capsule-max-artifact-mb CAPSULE_MAX_ARTIFACT_MB
                        Max artifact size in MB (default: 10).
```

## `oss-paper-ci capsule`

Capsule management (verify, inspect, diff).

```
usage: oss-paper-ci capsule [-h] {verify,inspect,diff} ...

positional arguments:
  {verify,inspect,diff}
    verify              Verify capsule integrity.
    inspect             Inspect capsule contents.
    diff                Compare two capsules.

options:
  -h, --help            show this help message and exit
```

## `oss-paper-ci init`

Generate config or contract templates.

```
usage: oss-paper-ci init [-h] [--contract] [--profile PROFILE]
                         [--template {ml,simulation,data-science,default}]
                         [--output OUTPUT] [--force] [--dry-run]

options:
  -h, --help            show this help message and exit
  --contract            Generate reproducibility.yml template
  --profile PROFILE     Policy profile for generated config.
  --template {ml,simulation,data-science,default}
  --output OUTPUT, -o OUTPUT
                        Output file path
  --force               Overwrite existing file.
  --dry-run             Print config to stdout instead of writing.
```

## `oss-paper-ci config`

Configuration management.

```
usage: oss-paper-ci config [-h] {validate,init,explain} ...

positional arguments:
  {validate,init,explain}
    validate            Validate a config file.
    init                Generate a default config file.
    explain             Show the resolved configuration.

options:
  -h, --help            show this help message and exit
```

## `oss-paper-ci diff`

Compare two scan reports.

```
usage: oss-paper-ci diff [-h] --old OLD --new NEW_REPORT
                         [--format {json,markdown}] [--output OUTPUT]

options:
  -h, --help            show this help message and exit
  --old OLD             Path to old report JSON.
  --new NEW_REPORT      Path to new report JSON.
  --format {json,markdown}
                        Output format.
  --output OUTPUT, -o OUTPUT
                        Write output to file.
```

## `oss-paper-ci doctor`

Diagnose repository and environment.

```
usage: oss-paper-ci doctor [-h] [--format {json,markdown}] [path]

positional arguments:
  path                  Path to repository root (default: .)

options:
  -h, --help            show this help message and exit
  --format {json,markdown}
                        Output format.
```

## `oss-paper-ci graph`

Build and display evidence graph.

```
usage: oss-paper-ci graph [-h] [--format {json,markdown,dot}]
                          [--output OUTPUT] [--show-orphans]
                          [--show-conflicts]
                          [path]

positional arguments:
  path

options:
  -h, --help            show this help message and exit
  --format {json,markdown,dot}
  --output OUTPUT, -o OUTPUT
  --show-orphans
  --show-conflicts
```

## `oss-paper-ci baseline`

Baseline management.

```
usage: oss-paper-ci baseline [-h] {create,compare} ...

positional arguments:
  {create,compare}
    create          Create a baseline from current scan.
    compare         Compare current scan against a baseline.

options:
  -h, --help        show this help message and exit
```

## `oss-paper-ci smoke`

Run smoke tests safely.

```
usage: oss-paper-ci smoke [-h] [--contract CONTRACT] [--experiment EXPERIMENT]
                          [--timeout TIMEOUT] [--dry-run]
                          [--command SMOKE_COMMAND] [--format {json,text}]
                          [path]

positional arguments:
  path                  Path to repository root (default: .)

options:
  -h, --help            show this help message and exit
  --contract CONTRACT   Path to reproducibility.yml contract file.
  --experiment EXPERIMENT
                        Experiment ID to run (default: smoke)
  --timeout TIMEOUT     Timeout in seconds (default: 60)
  --dry-run             Show the command without executing it.
  --command SMOKE_COMMAND
                        Override the smoke command (instead of reading from
                        contract).
  --format {json,text}  Output format (default: text)
```

## `oss-paper-ci workspace`

Workspace management.

```
usage: oss-paper-ci workspace [-h] {validate,list} ...

positional arguments:
  {validate,list}
    validate       Validate a workspace file.
    list           List projects in a workspace.

options:
  -h, --help       show this help message and exit
```

## `oss-paper-ci batch`

Batch scanning.

```
usage: oss-paper-ci batch [-h] {scan,diff} ...

positional arguments:
  {scan,diff}
    scan       Scan all projects in a workspace.
    diff       Compare two batch reports.

options:
  -h, --help   show this help message and exit
```

## `oss-paper-ci rules`

Rule pack management.

```
usage: oss-paper-ci rules [-h] {validate,list} ...

positional arguments:
  {validate,list}
    validate       Validate a rule pack manifest.
    list           List rules in a rule pack.

options:
  -h, --help       show this help message and exit
```

## `oss-paper-ci cache`

Cache management.

```
usage: oss-paper-ci cache [-h] {clean,info} ...

positional arguments:
  {clean,info}
    clean       Remove all cached results.
    info        Show cache statistics.

options:
  -h, --help    show this help message and exit
```

## `oss-paper-ci explain`

Explain a check or policy profile.

```
usage: oss-paper-ci explain [-h] target [extra]

positional arguments:
  target      Check ID (e.g., ENV001) or 'policy <name>'.
  extra       Profile name when target is 'policy'.

options:
  -h, --help  show this help message and exit
```

## `oss-paper-ci list-checks`

List all available checks.

```
usage: oss-paper-ci list-checks [-h] [--category CATEGORY]
                                [--format {text,json}]

options:
  -h, --help            show this help message and exit
  --category CATEGORY   Filter by category (e.g., metadata, environment).
  --format {text,json}  Output format.
```

## `oss-paper-ci validate-contract`

Validate a reproducibility contract.

```
usage: oss-paper-ci validate-contract [-h] [--contract CONTRACT] [path]

positional arguments:
  path

options:
  -h, --help           show this help message and exit
  --contract CONTRACT  Path to reproducibility.yml
```

## `oss-paper-ci comment`

Generate PR comment from scan results.

```
usage: oss-paper-ci comment [-h] --input INPUT [--output OUTPUT]
                            [--kind {scan,baseline}]
                            [--max-findings MAX_FINDINGS]

options:
  -h, --help            show this help message and exit
  --input INPUT         Path to scan JSON report.
  --output OUTPUT, -o OUTPUT
                        Write comment to file instead of stdout.
  --kind {scan,baseline}
                        Comment type.
  --max-findings MAX_FINDINGS
                        Max findings to show.
```

## `oss-paper-ci version`

Print version.

```
usage: oss-paper-ci version [-h]

options:
  -h, --help  show this help message and exit
```
