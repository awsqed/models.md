# GitHub Copilot Instructions

## Priority Guidelines

When generating code for this repository, follow this priority order:

1. Version compatibility and dependency constraints in this document.
2. Any files under `.github/copilot/` (if more are added later).
3. Established patterns in `src/models_pipeline/` and `tests/`.
4. Existing data contracts in `models.schema.yaml` and `config.json`.
5. Consistency with surrounding code over external best practices.

Do not introduce patterns that are not already present in this repository unless explicitly requested.

## Technology Versions

Use only features compatible with detected versions:

- Python: `>=3.14` (`pyproject.toml`, `pyrightconfig.json`).
- Package/build tools: `uv` + `hatchling` (`pyproject.toml`, `uv.lock`).
- LLM SDKs used by code:
  - `openai==2.29.0`
  - `anthropic==0.86.0`
  - `google-genai==1.68.0`
- Source/data utilities:
  - `crawl4ai==0.8.5`
  - `markdownify==1.2.2`
  - `python-dotenv==1.2.2`
  - `python-toon==0.1.3`
- QA/test tooling in active use:
  - `pytest==9.0.2`
  - `pyright==1.1.408`
  - `ruff==0.15.7`
  - `ufmt==2.9.1`

Never assume newer APIs than the versions above.

## Architecture And Boundaries

Treat the codebase as a layered, modular monolith with clear package boundaries:

- `src/models_pipeline/config/`: configuration parsing, coercion, validation, and dataclass schema.
- `src/models_pipeline/sources/`: source parser abstraction, parser registry, and source reading/summarization flow.
- `src/models_pipeline/crawl/`: crawl4ai integration and markdown extraction.
- `src/models_pipeline/prompt/`: prompt construction for catalog generation and source summarization.
- `src/models_pipeline/llm/`: provider router, provider backends, and retry executor.
- `src/models_pipeline/output/`: JSON extraction/parsing/validation and write-or-check output handling.
- `src/models_pipeline/pipeline/`: orchestration of end-to-end steps plus run logging and artifacts.
- `src/models_pipeline/cli.py` and `src/models_pipeline/__main__.py`: CLI entrypoints.

Keep responsibilities in their current package:

- Do not place HTTP/provider logic outside `llm/` and `sources/http.py`.
- Do not move orchestration logic out of `pipeline/run_session.py`.
- Do not bypass `sources.registry` when adding source types.
- Do not bypass `output.parse` + `output.validate` contracts when handling LLM responses.

## Observed Code Patterns

Follow these repository-native conventions.

### Imports And Module Organization

- Use absolute imports rooted at `models_pipeline`.
- Keep imports grouped and stable; avoid wildcard imports.
- Use `__all__` in package `__init__.py` files when exposing package-level API.

### Typing And Data Modeling

- Add type hints on public function signatures and important internal helpers.
- Use frozen dataclasses for immutable request/config DTOs (`ChatRequest`, `PipelineOptions`, `SourceItem`, etc.).
- Use union syntax (`A | B`) and built-in generics (`list[str]`, `dict[str, object]`).

### Error Handling

- Use `ValueError` for invalid user/config input and contract violations.
- Use `RuntimeError` for runtime failures (network, external services, unsupported runtime state).
- In LLM backends, map SDK-specific exceptions into `LLMRetryableError`/`LLMFatalError`, then normalize to `RuntimeError` in executor flow.

### Logging And Runtime Feedback

- Use concise `print(...)` status lines with prefixes like `[step]`, `[llm]`, `[source]`, `[output]`.
- Use `RunLogger` and artifact writers for structured run diagnostics under `logs/runs/`.
- Do not introduce Python `logging` module in new code unless explicitly requested.

### File And Path Handling

- Use `pathlib.Path` for path operations.
- Read/write text with explicit `encoding="utf-8"`.
- Create parent directories with `mkdir(parents=True, exist_ok=True)` before writes.
- Preserve workspace safety checks (for example, preventing file-source path escape).

### Prompt/Output Contract Rules

- Prompt builders return `(system_prompt, user_prompt)` tuple.
- LLM output is expected to be a single JSON object mapping output path -> markdown content.
- Output markdown values must be non-empty and newline-terminated.
- Output names must be restricted to configured allowed outputs.

## Testing Conventions

Mirror existing `pytest` style:

- Test files/functions use `test_` naming.
- Use plain function tests, not test classes.
- Use fixtures like `tmp_path`, `monkeypatch`, `capsys`.
- Prefer explicit assertion of behavior and error messages (`pytest.raises(..., match=...)`).
- For flow/orchestration tests, patch call sites with `monkeypatch.setattr` and assert call order or captured artifacts.

When adding behavior:

- Add/adjust unit tests in `tests/` near the affected module area (`tests/config`, `tests/pipeline`, `tests/sources`, etc.).
- Keep tests deterministic and local (no real network/API calls unless intentionally testing adapters with mocks/stubs).

## Documentation Requirements

Documentation style in this repository is minimal and practical:

- Add docstrings for modules and key public functions where behavior is not obvious.
- Keep comments short and focused on intent or invariants.
- Avoid verbose narrative comments or restating obvious code.

## Concrete Examples From This Repo

Use these as pattern anchors:

- CLI shape: `parse_args() -> argparse.Namespace`, `main() -> int`, and `raise SystemExit(main())` entrypoint.
  - See: `src/models_pipeline/cli.py`, `src/models_pipeline/__main__.py`
- Immutable config and request objects via frozen dataclasses.
  - See: `src/models_pipeline/config/schema.py`, `src/models_pipeline/llm/types.py`, `src/models_pipeline/pipeline/types.py`
- Registry-driven source type support with parser interface and explicit registration.
  - See: `src/models_pipeline/sources/base.py`, `src/models_pipeline/sources/registry.py`, `src/models_pipeline/sources/parsers.py`
- Step-oriented pipeline orchestration with structured run artifacts and JSON step logs.
  - See: `src/models_pipeline/pipeline/run_session.py`, `src/models_pipeline/pipeline/log_runner.py`
- Strict parse-validate-write output flow.
  - See: `src/models_pipeline/output/parser.py`, `src/models_pipeline/output/validator.py`, `src/models_pipeline/output/writer.py`
- Retry/backoff and backend routing for LLM calls.
  - See: `src/models_pipeline/llm/executor.py`, `src/models_pipeline/llm/router.py`, `src/models_pipeline/llm/backends/*.py`
- Pytest monkeypatch-heavy orchestration tests.
  - See: `tests/pipeline/test_pipeline_run_session.py`, `tests/test_llm_client.py`, `tests/test_output.py`

## Dependency And Versioning Guidelines

- Treat project versioning as semantic (current version `0.1.0` in `pyproject.toml`).
- If code changes require new dependencies or APIs:
  - Update `pyproject.toml` dependency declarations.
  - Refresh and commit `uv.lock`.
  - Keep generated code compatible with Python 3.14 and the locked package versions.

## Build, QA, And Local Commands

Prefer existing commands in `Makefile`:

- `make run` / `make check`
- `make test`
- `make lint`
- `make typecheck`
- `make qa`

Do not invent new command flows when existing targets already cover the task.

## Final Rule

Before producing non-trivial code, scan neighboring files in the same package and mirror:

- naming,
- typing precision,
- exception style,
- logging format,
- and test structure.

If uncertain, prefer strict consistency with existing repository patterns over introducing new abstractions.
