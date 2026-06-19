# Docker

Docker is an **optional** way to run oss-paper-ci. The tool is a Python CLI that can be installed directly via pip or from source.

## Quick Start

```bash
# Build the image
docker build -t oss-paper-ci:local .

# Show quickstart
docker run --rm oss-paper-ci:local

# Scan your project
docker run --rm -v "$PWD:/work" oss-paper-ci:local scan /work
```

## Building the Image

```bash
docker build -t oss-paper-ci:local .
```

This creates a minimal image with:
- Python 3.12
- oss-paper-ci installed
- Non-root user
- Default entrypoint: `oss-paper-ci quickstart`

## Usage Examples

### Scan a local directory

```bash
docker run --rm -v "$(pwd):/work" oss-paper-ci:local scan /work
```

### Run the built-in demo

```bash
docker run --rm oss-paper-ci:local try-demo
```

### Interactive shell

```bash
docker run --rm -it --entrypoint /bin/bash oss-paper-ci:local
```

### Generate a report

```bash
docker run --rm -v "$(pwd):/work" oss-paper-ci:local scan /work --format json --output /work/report.json
```

## Docker Compose

```yaml
version: "3.8"
services:
  oss-paper-ci:
    build: .
    volumes:
      - .:/work
    working_dir: /work
    command: scan /work
```

## Important Notes

- The image is for local testing only (not published anywhere)
- No external network access is required
- The container runs as a non-root user

## When to Use Docker

Use Docker when:
- You want a reproducible environment
- You don't want to install Python dependencies locally
- You're testing in CI/CD

Don't use Docker when:
- You're developing oss-paper-ci itself (use `pip install -e ".[dev]"`)
- You need fast iteration (direct install is faster)
