# Synthetic Makefile for test fixture
# This is a minimal Makefile for oss-paper-ci evaluation.

.PHONY: reproduce clean analyze

reproduce: analyze

analyze:
	@echo "Running analysis..."
	@bash scripts/run.sh

clean:
	@echo "Cleaning up results..."
	@rm -f results/results.json
