# Dev Container

A dev container provides a pre-configured development environment for oss-paper-ci.

## Quick Start

1. Install the [Dev Containers extension](https://marketplace.visualstudio.com/items?itemName=ms-vscode-remote.remote-containers) in VS Code
2. Open the oss-paper-ci repository
3. Click "Reopen in Container" when prompted
4. Wait for the container to build

The container will:
- Install Python 3.12
- Install oss-paper-ci in development mode
- Verify the installation

## What's Included

- Python 3.12
- Git
- oss-paper-ci with dev dependencies
- VS Code Python extension

## After Container Setup

```bash
# Verify installation
oss-paper-ci version

# Run the demo
oss-paper-ci try-demo

# Run tests
python -m pytest
```

## Customization

Edit `.devcontainer/devcontainer.json` to:
- Change Python version
- Add more VS Code extensions
- Modify post-create commands

## Troubleshooting

If the container fails to build:
1. Check Docker is running
2. Check internet connection
3. Try rebuilding: "Dev Containers: Rebuild Container"
