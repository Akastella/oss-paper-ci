# Glossary

Terms used in oss-paper-ci documentation.

## A

**attempted reproduction** — Running the declared reproduction commands
from a repository. This is an *attempt*, not a guarantee of success.

## C

**capsule** — A self-contained evidence package containing reproduction
reports, logs, metadata, and SHA256 integrity checksums. Also called
"reproduction capsule."

**check** — A single reproducibility readiness assessment (e.g., "Does
the repository have a README?").

**check result** — The outcome of a single check: pass, warn, or fail.

## E

**evidence package** — Another term for a capsule. Contains evidence of
what was done during a reproduction attempt.

## G

**guided mode** — Interactive guidance provided by `oss-paper-ci guide`,
tailored to the user's role and topic of interest.

## P

**plain-language summary** — A human-readable summary of a reproduction
attempt, avoiding technical jargon.

**policy profile** — A set of thresholds and severity overrides that
determine how strict the scan is. Profiles: lenient, default, strict,
publication.

## R

**readiness check** — An assessment of whether a repository has the
engineering basics needed for reproducibility.

**reproduction attempt** — Running the declared reproduction commands.
Success means the commands completed, not that the paper is correct.

**reproduction capsule** — See "capsule."

**reproduction contract** — A YAML file (reproducibility.yml) that
declares how to reproduce a paper's computational results.

**rule pack** — A YAML file defining custom checks without writing Python.

## S

**scan** — Running oss-paper-ci's checks on a repository to assess
reproducibility readiness.

**score** — A 0-100 numeric assessment of reproducibility readiness.
Higher is better, but does not guarantee correctness.

## See Also

- [Failure Taxonomy](failure-taxonomy.md)
- [Human-Centered Reproducibility](human-centered-reproducibility.md)
- [Roles](roles.md)
