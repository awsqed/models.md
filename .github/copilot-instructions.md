# Copilot Instructions for `models-pipeline`

## Build, test, and lint commands

- Preferred task runner:
  - `make help`
  - `make setup`
  - `make run` (set `OPENAI_API_KEY`)
  - `make check` (set `OPENAI_API_KEY`)
  - `make qa`
  - `make test-file TEST=tests/test_pipeline.py`
  - `make test-case TEST=tests/test_pipeline.py::test_step_load_config_reads_and_overrides`

- Initial setup (installs deps and crawl runtime):
  - `uv sync && uv run crawl4ai-setup`
- Run CLI help:
  - `uv run python -m models_pipeline --help`
  - `uv run models-pipeline --help`
- Generate outputs:
  - `OPENAI_API_KEY=... uv run models-pipeline`
- Validate outputs without writing:
  - `OPENAI_API_KEY=... uv run models-pipeline --check`

- Full test suite:
  - `uv run pytest`
- Single test file:
  - `uv run pytest tests/test_pipeline.py`
- Single test case:
  - `uv run pytest tests/test_pipeline.py::test_step_load_config_reads_and_overrides`

- Lint:
  - `uv run ruff check src tests`
- Type check:
  - `uv run pyright src`

## Skills

- Add source type: `.github/skills/add-source-type/SKILL.md`
- Conventional commit: `.github/skills/conventional-commit/SKILL.md`

## High-level architecture

This project is a typed pipeline that regenerates markdown catalogs from local files, crawled URLs, and models.dev API data.

- Entrypoints:
  - `models-pipeline` script (`pyproject.toml`) -> `models_pipeline.cli:main`
  - `python -m models_pipeline` -> `src/models_pipeline/__main__.py`
- Runtime orchestrator:
  - `src/models_pipeline/pipeline/run_session.py` creates per-run logs under `logs/runs/<timestamp>/`, executes steps, and supports write mode vs `--check`.
- Pipeline steps:
  - `src/models_pipeline/pipeline/step_config.py`, `step_read.py`, and `step_process.py` implement load config -> optional crawl dependency check -> load schema -> read/summarize sources -> build prompt -> call LLM -> parse outputs -> validate/write outputs.
- Config and schema:
  - `config.json` is loaded by `src/models_pipeline/config/loader.py` into frozen dataclasses in `config/schema.py`, which also define the runtime defaults.
  - Output paths are dynamic but constrained to `docs/models/*.md`.
- Source ingestion:
  - `src/models_pipeline/sources/reader.py` dispatches by registry-backed parser kind.
  - built-in source types: `file`, `url`, `text`, `models_dev_api`.
  - URL sources use crawl integration in `src/models_pipeline/crawl/`.
  - models.dev ingestion is in `src/models_pipeline/sources/http.py`.
- Prompting + LLM:
  - Catalog prompts in `src/models_pipeline/prompt/catalog.py`; optional per-source summarization prompt in `prompt/summarizer.py`.
  - `src/models_pipeline/llm/adapter_select.py` + `src/models_pipeline/llm/request_exec.py` auto-detect OpenAI vs Anthropic-style adapter from base URL and perform retry/error handling.
- Output handling:
  - LLM response must be JSON mapping output file path -> markdown content.
  - Parsing and guardrails are in `src/models_pipeline/output/parser.py` and `output/validator.py`.
  - File write/check behavior is in `output/writer.py`.

## Key conventions in this repository

- `config.json` shape is flat (no nested `runtime` object): top-level `llm`, `summarizer`, `logging`, `max_chars_per_source`, `outputs`, `sources`.
  - `llm` and `summarizer` both accept `model`, `api_base_url`, `timeout_seconds`, `max_retries`, `max_output_tokens`, and `disable_thinking`.
  - `sources[]` entries use `name`, `type`, `value`, optional `summarize`, optional `browser`, optional `run`, and optional `to_toon` for `models_dev_api`.
- Source kinds come from `src/models_pipeline/sources/registry.py` registrations.
- URL source conventions:
  - A source must specify a single `value` URL; `urls` is not supported.
  - The `query` and `adaptive` fields are not supported.
- File source safety:
  - File sources are restricted to workspace-relative paths; escaping repository root raises an error.
- Output contract:
  - Output names must be unique and match `docs/models/*.md`.
  - LLM output must include all expected outputs and no extras.
  - Markdown values are normalized to end with newline.
- LLM auth behavior:
  - Default key env is `OPENAI_API_KEY`.
  - If adapter resolves to Anthropic and request kept default key env, client auto-switches to `ANTHROPIC_API_KEY`.
- Optional source summarization:
  - Each source can set `summarize: true|false`; when omitted, it falls back to global `summarizer.enabled`.
- Logging conventions:
  - Runs always emit structured artifacts in `logs/runs/...` (`run.meta.json`, `config.resolved.json`, step input/output JSON, status/events).
  - Extra logging payloads are gated by `logging.capture_sources`, `capture_prompts`, `capture_llm_io`, `capture_outputs`.
