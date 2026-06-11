# Evidence Map

The evidence map is a structured inventory of reproducibility evidence
in a repository.

## Categories

| Category | What it covers |
|----------|---------------|
| metadata | README, license, citation, project metadata |
| environment | requirements.txt, pyproject.toml, dependency declarations |
| data | data documentation, download instructions, external data notes |
| execution | declared commands, smoke tests, scripts |
| results | metrics, figures, tables, artifact index |
| provenance | commit SHA, capsule manifest, hashes, timestamps |
| automation | CI workflows, batch scanning, policy profiles |

## Status Values

| Status | Meaning |
|--------|---------|
| present | Evidence exists and is adequate |
| missing | Evidence does not exist |
| partial | Evidence exists but is incomplete |
| unknown | Could not determine |

## How It's Built

The evidence map is constructed by analyzing:
- Scan report check results
- Reproduce report metadata
- Capsule inspection data

## See Also

- [Dossier](dossier.md)
- [Remediation Plan](remediation-plan.md)
