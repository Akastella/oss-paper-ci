# Failure Taxonomy

When a reproduction attempt fails, understanding *why* it failed is as
important as knowing *that* it failed. This document provides a structured
reference for common failure types.

## How to Use This Document

1. Find your failure type in the list below
2. Read the "Likely causes" to understand what went wrong
3. Follow the "Suggested next steps" to try to resolve it
4. Read "What this does not mean" to avoid over-interpreting the failure

## Failure Types

### source_resolution_failed

**What happened:** The repository URL or path could not be resolved.

**Likely causes:**
- The URL is malformed or incomplete
- The repository is private
- A paper URL was provided without `--repo`

**Next steps:**
- Check the URL format
- For paper URLs, use `--repo <github-url>`
- For local paths, verify the directory exists

**This does not mean:** The paper has no code, or the research is flawed.

---

### environment_missing

**What happened:** No environment files found in the repository.

**Likely causes:**
- No requirements.txt, pyproject.toml, or environment.yml
- Dependencies declared in an unsupported format

**Next steps:**
- Check the repository for dependency files
- Contact the author to add declarations

**This does not mean:** The code cannot run, or the research is invalid.

---

### dependency_install_failed

**What happened:** Dependencies could not be installed.

**Likely causes:**
- Package not available on PyPI
- Version conflicts
- Missing system dependencies

**Next steps:**
- Check error output for specific package failures
- Try installing manually in a clean environment

**This does not mean:** The code is broken. May be environment-specific.

---

### command_not_declared

**What happened:** No reproduction command found.

**Likely causes:**
- No reproducibility.yml
- No common scripts found

**Next steps:**
- Use `--command` to specify manually
- Check the README for instructions

**This does not mean:** The code cannot be reproduced.

---

### command_timeout

**What happened:** The command exceeded the time limit.

**Likely causes:**
- Command needs more time
- Waiting for input
- Stuck in a loop

**Next steps:**
- Increase timeout with `--timeout N`
- Check for interactive input requirements

**This does not mean:** The code is broken.

---

### command_failed

**What happened:** The command returned a non-zero exit code.

**Likely causes:**
- Runtime error
- Missing input data
- Incompatible versions

**Next steps:**
- Check stderr output
- Verify input files exist
- Check version compatibility

**This does not mean:** The paper's claims are wrong. May be environment-specific.

---

### artifact_missing

**What happened:** Expected output files were not generated.

**Likely causes:**
- Command did not complete
- Output path is different than expected

**Next steps:**
- Check if command completed successfully
- Look for outputs in alternative locations

**This does not mean:** The research failed.

---

### scan_blocking_findings

**What happened:** Scan found issues blocking reproducibility.

**Likely causes:**
- Missing README, license, or citation
- No environment files
- No experiment scripts

**Next steps:**
- Review scan report for specific findings
- Address errors first, then warnings

**This does not mean:** The research is bad. Means engineering basics are missing.

---

### capsule_integrity_failed

**What happened:** Capsule failed integrity verification.

**Likely causes:**
- Capsule was modified after creation
- Capsule was corrupted during transfer

**Next steps:**
- Re-generate the capsule
- Verify before sharing

**This does not mean:** The reproduction failed. Means the evidence package can't be verified.

---

### unsupported_environment

**What happened:** Repository requires an environment that can't be provided automatically.

**Likely causes:**
- Requires conda instead of pip
- Requires GPU
- Requires external data

**Next steps:**
- Check repository documentation for manual setup
- Install required environment manually

**This does not mean:** The research is not reproducible. Means automation isn't possible.

---

## See Also

- [Human-Centered Reproducibility](human-centered-reproducibility.md)
- [Roles](roles.md)
- [Glossary](glossary.md)
