# oss-paper-ci Dockerfile
# This is an OPTIONAL distribution method.
# oss-paper-ci is a Python CLI tool that can be installed directly via pip.
# This container provides a pre-built environment for quick testing.

FROM python:3.12-slim

LABEL maintainer="oss-paper-ci contributors"
LABEL description="oss-paper-ci: CI tool for scientific reproducibility"

# Install git (needed for some operations)
RUN apt-get update && \
    apt-get install -y --no-install-recommends git && \
    rm -rf /var/lib/apt/lists/*

# Create non-root user
RUN useradd --create-home --shell /bin/bash appuser
USER appuser
WORKDIR /home/appuser

# Copy project files
COPY --chown=appuser:appuser . /home/appuser/oss-paper-ci

# Install the package
RUN pip install --no-cache-dir /home/appuser/oss-paper-ci

# Default working directory for user projects
WORKDIR /work

# Default entrypoint shows quickstart
ENTRYPOINT ["oss-paper-ci"]
CMD ["quickstart"]
