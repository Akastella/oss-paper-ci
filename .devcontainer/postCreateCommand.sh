#!/bin/bash
# Post-create setup for oss-paper-ci devcontainer

set -e

echo "Installing oss-paper-ci in development mode..."
pip install -e ".[dev]"

echo "Verifying installation..."
oss-paper-ci version

echo ""
echo "=== oss-paper-ci devcontainer ready ==="
echo ""
echo "Try these commands:"
echo "  oss-paper-ci quickstart     # Get started"
echo "  oss-paper-ci try-demo       # Run built-in demo"
echo "  oss-paper-ci scan .         # Scan current directory"
echo "  oss-paper-ci wizard         # Guided setup"
echo ""
