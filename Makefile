.PHONY: minify unit-test test help

# Shared virtualenv lives in the sibling core checkout (same-folder layout).
PYTHON ?= ../ce-mongo-x-ray/.venv/bin/python

# Minify templates
minify:
	@echo "Minifying templates..."
	cd src/mongo_x_ray_log/templates && ./minify.sh
	@echo "\033[32m✓ Templates minified!\033[0m"

# Run the unit tests (excludes integration tests)
unit-test:
	@echo "Running unit tests..."
	$(PYTHON) -m pytest -m "not integration"
	@echo "\033[32m✓ All unit tests passed!\033[0m"

# Core-style alias for make test
test: unit-test

# Help information
help:
	@echo "mongo-x-ray-log Makefile"
	@echo ""
	@echo "Available commands:"
	@echo "  make minify      - Minify HTML/JS/CSS templates"
	@echo "  make unit-test   - Run the unit tests (non-integration)"
	@echo "  make test        - Alias for unit-test"
	@echo "  make help        - Display this help information"
