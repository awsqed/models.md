SHELL := /bin/bash

.DEFAULT_GOAL := help

SOURCES ?= config.json
MODEL ?=
API_BASE_URL ?=
TEST ?=
PY_PATHS := src tests

MODEL_ARG := $(if $(strip $(MODEL)),--model "$(MODEL)",)
API_BASE_URL_ARG := $(if $(strip $(API_BASE_URL)),--api-base-url "$(API_BASE_URL)",)
UNTIL_STEP_ARG := $(if $(strip $(UNTIL_STEP)),--until-step "$(UNTIL_STEP)",)

.PHONY: help setup sync crawl-setup install run check cli-help py-help test test-file test-case lint typecheck format format-check deadcode qa clean clean-logs

help:
	@echo "Available targets:"
	@echo "  make setup         - Install dependencies and crawl runtime"
	@echo "  make install       - Alias for setup"
	@echo "  make sync          - Install project dependencies with uv"
	@echo "  make crawl-setup   - Install crawl4ai runtime dependencies"
	@echo "  make run           - Generate outputs from $(SOURCES)"
	@echo "  make check         - Validate outputs without writing"
	@echo "  make cli-help      - Show CLI help from package entrypoint"
	@echo "  make py-help       - Show CLI help from python -m entrypoint"
	@echo "  make test          - Run full test suite"
	@echo "  make test-file     - Run tests in file (TEST=tests/test_pipeline.py)"
	@echo "  make test-case     - Run one test case (TEST=tests/test_pipeline.py::test_name)"
	@echo "  make lint          - Run Ruff checks"
	@echo "  make typecheck     - Run Pyright type checks"
	@echo "  make format        - Format code with ufmt"
	@echo "  make format-check  - Check formatting with ufmt"
	@echo "  make deadcode      - Check for unused code with vulture"
	@echo "  make qa            - Run lint + typecheck + test"
	@echo "  make clean-logs    - Remove generated run logs"
	@echo "  make clean         - Alias for clean-logs"
	@echo ""
	@echo "Variables:"
	@echo "  SOURCES=<path>     Config file path (default: config.json)"
	@echo "  MODEL=<name>       Override configured model"
	@echo "  API_BASE_URL=<url> Override configured API base URL"
	@echo "  UNTIL_STEP=<step>  Run pipeline until specified step (e.g. 'generate')"
	@echo "  TEST=<selector>    Pytest selector for test-file/test-case"

sync:
	uv sync

crawl-setup:
	uv run crawl4ai-setup

setup: sync crawl-setup

install: setup

run:
	uv run models-pipeline --sources "$(SOURCES)" $(MODEL_ARG) $(API_BASE_URL_ARG) $(UNTIL_STEP_ARG)

check:
	uv run models-pipeline --sources "$(SOURCES)" --check $(MODEL_ARG) $(API_BASE_URL_ARG) $(UNTIL_STEP_ARG)

cli-help:
	uv run models-pipeline --help

py-help:
	uv run python -m models_pipeline --help

test:
	uv run pytest

test-file:
	@if [ -z "$(TEST)" ]; then echo "Set TEST=tests/test_file.py"; exit 1; fi
	uv run pytest "$(TEST)"

test-case:
	@if [ -z "$(TEST)" ]; then echo "Set TEST=tests/test_file.py::test_name"; exit 1; fi
	uv run pytest "$(TEST)"

lint:
	uv run ruff check $(PY_PATHS)

typecheck:
	uv run pyright src

format:
	uv run ufmt format $(PY_PATHS)

format-check:
	uv run ufmt check $(PY_PATHS)

deadcode:
	uv run vulture src --min-confidence 90

qa: lint typecheck test

clean-logs:
	rm -rf logs/runs

clean: clean-logs
