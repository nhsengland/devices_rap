#################################################################################
# GLOBALS                                                                       #
#################################################################################

PROJECT_NAME = devices_rap
PYTHON_VERSION = 3.12

# Detect if uv is available
UV_AVAILABLE := $(shell command -v uv >/dev/null 2>&1 && echo "yes" || echo "no")

# Environment variables that can be overridden
USE_UV ?= auto
VENV_DIR ?= .venv

# Determine which tool to use
ifeq ($(USE_UV),yes)
    TOOL = uv
else ifeq ($(USE_UV),no)
    TOOL = venv
else ifeq ($(UV_AVAILABLE),yes)
    TOOL = uv
else
    TOOL = venv
endif

# Set commands based on tool choice
ifeq ($(TOOL),uv)
    PYTHON_INTERPRETER = uv run python
    VENV_CREATE = uv venv $(VENV_DIR)
    INSTALL_CMD = uv sync
    INSTALL_DEV = uv sync --extra dev
    INSTALL_ALL = uv sync --extra dev --extra docs --extra jupyter
else
    PYTHON_INTERPRETER = $(VENV_DIR)/bin/python
    VENV_CREATE = python -m venv $(VENV_DIR)
    INSTALL_CMD = $(PYTHON_INTERPRETER) -m pip install -e .
    INSTALL_DEV = $(PYTHON_INTERPRETER) -m pip install -e ".[dev]"
    INSTALL_ALL = $(PYTHON_INTERPRETER) -m pip install -e ".[dev,docs,jupyter]"
endif

#################################################################################
# COMMANDS                                                                      #
#################################################################################

## Show environment info
.PHONY: info
info:
	@echo "=== Environment Information ==="
	@echo "Project: $(PROJECT_NAME)"
	@echo "Tool: $(TOOL)"
	@echo "UV Available: $(UV_AVAILABLE)"
	@echo "Python Interpreter: $(PYTHON_INTERPRETER)"
	@echo "Virtual Environment: $(VENV_DIR)"
	@echo "================================"

## Create virtual environment (use USE_UV=yes/no to force tool choice)
.PHONY: venv
venv:
	@echo "Creating virtual environment with $(TOOL)..."
ifeq ($(TOOL),uv)
	$(VENV_CREATE)
	@echo "✓ Virtual environment created with uv"
	@echo "To activate: source $(VENV_DIR)/bin/activate"
	@echo "Or use: uv run <command>"
else
	$(VENV_CREATE)
	$(VENV_DIR)/bin/python -m pip install --upgrade pip
	@echo "✓ Virtual environment created with venv"
	@echo "To activate: source $(VENV_DIR)/bin/activate"
endif

## Install production dependencies only
.PHONY: install
install: venv
	@echo "Installing production dependencies with $(TOOL)..."
	$(INSTALL_CMD)
	@echo "✓ Production dependencies installed"

## Install development dependencies
.PHONY: install-dev
install-dev: venv
	@echo "Installing development dependencies with $(TOOL)..."
	$(INSTALL_DEV)
	@echo "✓ Development dependencies installed"

## Install all dependencies (dev + test + docs)
.PHONY: install-all
install-all: venv
	@echo "Installing all dependencies with $(TOOL)..."
	$(INSTALL_ALL)
	@echo "✓ All dependencies installed"

## Alias for install-dev (backward compatibility)
.PHONY: requirements
requirements: install-dev

## Check if dev environment is ready (light check without recreating venv)
.PHONY: check-dev-env
check-dev-env:
ifeq ($(TOOL),uv)
	@echo "Checking dev environment with uv..."
	@uv run python -c "import black, flake8, isort, pytest" 2>/dev/null || (echo "Dev dependencies missing, installing..." && $(MAKE) install-dev)
else
	@echo "Checking dev environment with venv..."
	@test -f $(VENV_DIR)/bin/python || $(MAKE) install-dev
	@$(PYTHON_INTERPRETER) -c "import black, flake8, isort, pytest" 2>/dev/null || $(MAKE) install-dev
endif

## Clean compiled Python files and caches
.PHONY: clean
clean:
	@echo "Cleaning Python artifacts..."
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type d -name "__pycache__" -delete
	find . -type d -name ".pytest_cache" -exec rm -rf {} +
	rm -rf htmlcov/
	rm -rf .coverage
	@echo "✓ Cleaned Python artifacts"

## Alias for clean
.PHONY: clear
clear: clean

## Remove virtual environment and lock files
.PHONY: clean-env
clean-env:
	@echo "Removing virtual environment and lock files..."
	rm -rf $(VENV_DIR)
	rm -f uv.lock
	rm -rf .uv
	@echo "✓ Environment cleaned"

## Complete cleanup (clean + clean-env)
.PHONY: nuke
nuke: clean clean-env
	@echo "🚀 Complete cleanup finished"

## Set up pre-commit hooks
.PHONY: pre-commit
pre-commit: check-dev-env
	@echo "Setting up pre-commit hooks..."
	$(PYTHON_INTERPRETER) -m pre_commit install
	@echo "✓ Pre-commit hooks installed"

## Run pre-commit on all files
.PHONY: pre-commit-all
pre-commit-all: check-dev-env
	@echo "Running pre-commit on all files..."
	$(PYTHON_INTERPRETER) -m pre_commit run --all-files

## Alias for pre-commit (backward compatibility)
.PHONY: pre-commits
pre-commits: pre-commit-all

## Lint code (without fixing)
.PHONY: lint
lint: check-dev-env
	@echo "Linting code..."
	$(PYTHON_INTERPRETER) -m flake8 $(PROJECT_NAME) tests/
	$(PYTHON_INTERPRETER) -m isort --check-only --diff --profile black $(PROJECT_NAME) tests/
	$(PYTHON_INTERPRETER) -m black --check --config pyproject.toml $(PROJECT_NAME) tests/

## Format code
.PHONY: format
format: check-dev-env
	@echo "Formatting code..."
	$(PYTHON_INTERPRETER) -m isort --profile black $(PROJECT_NAME) tests/
	$(PYTHON_INTERPRETER) -m black --config pyproject.toml $(PROJECT_NAME) tests/
	@echo "✓ Code formatted"

## Create a new branch
.PHONY: branch
branch:
	git checkout -b ${name}

## Create test files for all python files in the project
.PHONY: create_tests
create_tests:
	@find $(PROJECT_NAME) -type f -name "*.py" | while read file; do \
		if [ $$(basename $$file) != "__init__.py" ]; then \
			new_path=tests/unittests/$$(echo $$file | sed 's|^[^/]*/||' | awk -F/ '{for(i=1;i<=NF;i++)$$i="test_"$$i; print}' OFS=/); \
			mkdir -p $$(dirname $$new_path); \
			if [ ! -f $$new_path ]; then \
				touch $$new_path; \
				echo "\"\"\"\nTests for $$(echo $$file | sed 's|/|.|g' | sed 's|\.py||')\n\"\"\"\nimport pytest\n" >> $$new_path; \
				echo "import $$(echo $$file | sed 's|/|.|g' | sed 's|\.py||')" >> $$new_path; \
				echo "\n\nclass TestExample:" >> $$new_path; \
				echo "    \"\"\"Example test class\"\"\"" >> $$new_path; \
				echo "    def test_example(self):" >> $$new_path; \
				echo "        \"\"\"Example test case\"\"\"" >> $$new_path; \
				echo "        assert True" >> $$new_path; \
			fi \
		fi \
	done

#################################################################################
# DOCUMENTATION                                                                 #
#################################################################################

## Generate API reference documentation files
.PHONY: docs-generate
docs-generate: check-dev-env
	@echo "Generating API documentation..."
	$(PYTHON_INTERPRETER) docs/gen_ref_pages.py

## Build documentation
.PHONY: docs-build
docs-build: check-dev-env
	@echo "Building documentation..."
	$(PYTHON_INTERPRETER) -m mkdocs build --config-file docs/mkdocs.yml

## Serve documentation locally
.PHONY: docs-serve
docs-serve: check-dev-env
	@echo "Serving documentation locally..."
	$(PYTHON_INTERPRETER) -m mkdocs serve --config-file docs/mkdocs.yml

## Generate API docs and serve locally
.PHONY: docs
docs: docs-generate docs-serve

#################################################################################
# PROJECT RULES                                                                 #
#################################################################################

## Run pipeline in local mode
.PHONY: run-pipeline-local
run-pipeline-local: install
	@echo "Running pipeline in local mode..."
	$(PYTHON_INTERPRETER) -m $(PROJECT_NAME).pipeline --mode local

## Run pipeline in remote mode
.PHONY: run-pipeline-remote
run-pipeline-remote: install
	@echo "Running pipeline in remote mode..."
	$(PYTHON_INTERPRETER) -m $(PROJECT_NAME).pipeline --mode remote

## Run pipeline (default mode)
.PHONY: run
run: run-pipeline-local

## Run all tests
.PHONY: test
test: check-dev-env
	@echo "Running all tests..."
	$(PYTHON_INTERPRETER) -m pytest tests/ -v

## Run unit tests only
.PHONY: test-unit
test-unit: check-dev-env
	@echo "Running unit tests..."
	$(PYTHON_INTERPRETER) -m pytest tests/unittests/ -v

## Alias for test-unit (backward compatibility)
.PHONY: unittest
unittest: test-unit

## Run end-to-end tests only
.PHONY: test-e2e
test-e2e: check-dev-env
	@echo "Running e2e tests..."
	$(PYTHON_INTERPRETER) -m pytest tests/e2e_tests/ -v

## Alias for test-e2e (backward compatibility)
.PHONY: e2e
e2e: test-e2e

## Run tests with coverage
.PHONY: test-cov
test-cov: check-dev-env
	@echo "Running tests with coverage..."
	$(PYTHON_INTERPRETER) -m pytest tests/ --cov=$(PROJECT_NAME) --cov-report=html --cov-report=term-missing -v
	@echo "✓ Coverage report generated in htmlcov/"

#################################################################################
# Self Documenting Commands                                                     #
#################################################################################

.DEFAULT_GOAL := help

## Show available commands
.PHONY: help
help:
	@echo "$(PROJECT_NAME) - Available Commands"
	@echo ""
	@echo "Environment Setup:"
	@echo "  info         Show environment information"
	@echo "  venv         Create virtual environment"
	@echo "  install      Install production dependencies"
	@echo "  install-dev  Install development dependencies"
	@echo "  install-all  Install all dependencies (dev + docs + jupyter)"
	@echo "  requirements Install dev dependencies (alias for install-dev)"
	@echo ""
	@echo "Development:"
	@echo "  format       Format code with black and isort"
	@echo "  lint         Lint code without fixing"
	@echo "  pre-commit   Install pre-commit hooks"
	@echo "  pre-commit-all Run pre-commit on all files"
	@echo "  branch       Create new branch (usage: make branch name=branch-name)"
	@echo "  create_tests Create test files for Python modules"
	@echo ""
	@echo "Documentation:"
	@echo "  docs         Generate API docs and serve locally"
	@echo "  docs-generate Generate API reference files"
	@echo "  docs-build   Build documentation"
	@echo "  docs-serve   Serve documentation locally"
	@echo ""
	@echo "Testing:"
	@echo "  test         Run all tests"
	@echo "  test-unit    Run unit tests only"
	@echo "  test-e2e     Run end-to-end tests only"
	@echo "  test-cov     Run tests with coverage report"
	@echo "  unittest     Alias for test-unit"
	@echo "  e2e          Alias for test-e2e"
	@echo ""
	@echo "Pipeline:"
	@echo "  run          Run pipeline (default: local mode)"
	@echo "  run-pipeline-local  Run pipeline in local mode"
	@echo "  run-pipeline-remote Run pipeline in remote mode"
	@echo ""
	@echo "Cleanup:"
	@echo "  clean        Clean Python artifacts"
	@echo "  clear        Alias for clean"
	@echo "  clean-env    Remove virtual environment"
	@echo "  nuke         Complete cleanup (clean + clean-env)"
	@echo ""
	@echo "Environment Variables:"
	@echo "  USE_UV=yes/no/auto  Force tool choice (default: auto)"
	@echo "  VENV_DIR=path       Virtual environment directory (default: .venv)"
	@echo ""
	@echo "Examples:"
	@echo "  make info            # Show current environment"
	@echo "  make venv USE_UV=yes # Force use uv"
	@echo "  make venv USE_UV=no  # Force use venv"
	@echo "  make install-dev     # Auto-detect tool and install dev deps"
	@echo "  make branch name=jw/DEV-123_new-feature"
