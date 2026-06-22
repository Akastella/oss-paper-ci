# Paper URL Boundary

OSS-Paper-CI recognizes paper URLs (arXiv, DOI) but does not fetch or analyze paper content.

## Supported URL Types

### arXiv

```bash
oss-paper-ci intake https://arxiv.org/abs/2401.00001
```

### DOI

```bash
oss-paper-ci intake https://doi.org/10.1234/example
```

## Behavior

When a paper URL is provided:

1. The URL is recognized as a paper URL
2. A warning is generated: "Paper URL alone is not enough to reproduce; provide --repo or a local repository path."
3. No network request is made
4. No paper content is fetched or analyzed
5. No code repository is located

## What This Does NOT Do

- **Does not** fetch the paper PDF or HTML
- **Does not** extract code links from the paper
- **Does not** locate the associated code repository
- **Does not** analyze the paper's methodology
- **Does not** claim to find reproduction code

## Recommended Workflow

If you have a paper URL and want to reproduce its results:

1. Find the code repository manually (usually linked in the paper or on the author's website)
2. Clone the repository locally
3. Run intake on the local repository:

```bash
oss-paper-ci intake /path/to/cloned/repo
```

Or combine paper metadata with repository analysis:

```bash
oss-paper-ci intake /path/to/repo --output intake-report.md
```

## Future Work

Future versions may support:
- Extracting repository URLs from paper metadata
- Linking paper DOIs to code repositories
- Integrating with paper code indexes

These features are not yet implemented.
