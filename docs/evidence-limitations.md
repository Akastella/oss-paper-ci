# Evidence Report Limitations

## What This Report IS

- An engineering completeness assessment
- A snapshot of reproducibility artifacts at a point in time
- A starting point for human review
- A structured way to communicate "what evidence exists"

## What This Report IS NOT

- A scientific correctness proof
- A paper quality judgment
- An acceptance prediction
- A replacement for human review
- A security certification
- A signed attestation
- An official SBOM (SPDX/CycloneDX)

## Specific Limitations

### Scoring
- Score measures artifact presence, not correctness
- A score of 100 does not mean the research is reproducible
- A score of 0 does not mean the research is flawed
- Different profiles may emphasize different aspects

### Trust & Security
- Security scanning is pattern-based; may miss obfuscated secrets
- Workflow audit is static; does not verify runtime behavior
- Dependency inventory is based on declared metadata, not resolved versions
- No cryptographic signing or attestation

### Data & Results
- Checks for documentation presence, not content quality
- Does not verify data integrity or completeness
- Does not validate scientific claims
- Does not run experiments

### Reproduction
- Default mode is dry-run; does not execute code
- Even executed reproduction only runs commands the tool can detect
- Success does not guarantee correctness; failure does not indicate fraud

## Recommendations

1. Use this report as a conversation starter, not a verdict
2. Always perform manual review alongside automated checks
3. Consider the repository's specific context and constraints
4. Do not rely solely on automated tools for reproducibility assessment
