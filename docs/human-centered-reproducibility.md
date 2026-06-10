# Human-Centered Reproducibility

OSS-Paper-CI is designed to help people understand and improve the
reproducibility of scientific repositories. This document describes the
human-centered design principles behind the tool.

## Core Principles

### 1. Failure is Information

When a reproduction attempt fails, the failure report is valuable evidence.
It tells you:
- What was attempted
- Where it failed
- What the environment looked like
- What error messages were produced

A failure report is not a judgment on the research. It is data that can
help improve the repository.

### 2. Scores are Readiness, not Quality

A scan score of 90/100 means the repository has good engineering basics
for reproducibility. It does not mean:
- The paper is correct
- The results are valid
- The research is important

A score of 30/100 means the repository is missing engineering basics.
It does not mean:
- The paper is wrong
- The research is flawed
- The results are invalid

### 3. Reproduction is Evidence, not Proof

A successful reproduction attempt means the declared commands completed
in this environment. It does not mean:
- The paper's claims are correct
- The results will be the same in all environments
- The research is reproducible in the general sense

### 4. Roles Matter

Different people use oss-paper-ci for different reasons:

- **Authors** want to make their work easier to reproduce
- **Reviewers** want to assess reproducibility readiness
- **Maintainers** want to enforce standards

The tool provides role-specific guidance through `oss-paper-ci guide`.

### 5. Safety by Default

The tool defaults to safe behavior:
- Scanning is read-only
- Reproduction defaults to dry-run
- Code execution requires explicit `--execute`
- Dangerous commands are blocked

## What This Tool Does NOT Do

- Does not verify scientific correctness
- Does not judge paper quality or importance
- Does not guarantee numerical reproducibility
- Does not replace peer review
- Does not run experiments (unless explicitly asked)

## See Also

- [Failure Taxonomy](failure-taxonomy.md)
- [Roles](roles.md)
- [Glossary](glossary.md)
- [Security Model](security-model.md)
