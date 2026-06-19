#!/bin/bash
# Synthetic shell script for testing dry-run detection
# WARNING: This script contains risky patterns - DO NOT EXECUTE
# This is a test fixture for oss-paper-ci evaluation

# Risky pattern: curl | bash
# This downloads and executes remote code without verification
curl -s https://example.com/install.sh | bash

# Risky pattern: wget and execute
wget -qO- https://example.com/setup.sh | bash

echo "Script complete"
