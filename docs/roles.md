# Roles

OSS-Paper-CI serves different users with different needs. This document
describes the three primary roles and their recommended workflows.

## Author

**I am the paper/project author. I want my repository to be easier to reproduce.**

### Recommended Workflow

1. Scan your repository: `oss-paper-ci scan .`
2. Address blocking findings (errors)
3. Add a reproducibility.yml: `oss-paper-ci init --contract`
4. Re-scan to verify: `oss-paper-ci scan .`
5. Generate a capsule for sharing: `oss-paper-ci reproduce . --execute --install --capsule repro.zip`

### Key Concerns

- Make your repository easy for others to understand and run
- Document dependencies, data, and experiment commands
- Provide clear reproduction instructions

### Important Notes

- A high scan score does not prove your paper is correct
- Reproduction success depends on the environment, not just the code

---

## Reviewer

**I am a reviewer or reader. I want to assess reproducibility readiness.**

### Recommended Workflow

1. Scan the repository: `oss-paper-ci scan <repo>`
2. See what reproduction involves: `oss-paper-ci reproduce <repo> --dry-run`
3. Verify a capsule: `oss-paper-ci capsule verify <capsule.zip>`

### Key Concerns

- Check if dependencies are declared
- Check if experiment commands are documented
- Check the scan report for blocking issues

### Important Notes

- Scan results reflect engineering readiness, not scientific quality
- A low score does not mean the research is flawed
- Reproduction attempts are evidence, not proof

---

## Maintainer

**I maintain multiple repositories and want to enforce standards.**

### Recommended Workflow

1. Create a config: `oss-paper-ci config init --profile strict`
2. Set up a workspace: validate and list projects
3. Batch scan: `oss-paper-ci batch scan --workspace ws.yml`
4. Track changes: `oss-paper-ci baseline create/compare`

### Key Concerns

- Set realistic reproducibility standards
- Batch scan multiple repositories
- Track reproducibility over time

### Important Notes

- Standards should be realistic for your field
- Not all repositories need the same level of reproducibility

---

## See Also

- [Failure Taxonomy](failure-taxonomy.md)
- [Human-Centered Reproducibility](human-centered-reproducibility.md)
- [Glossary](glossary.md)
