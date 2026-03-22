import json
from pathlib import Path

from models_pipeline.config import (
    DEFAULT_LLM_API_BASE_URL,
    DEFAULT_LLM_MAX_OUTPUT_TOKENS,
    DEFAULT_LLM_MAX_RETRIES,
    DEFAULT_LLM_MODEL,
    DEFAULT_LLM_TIMEOUT_SECONDS,
    DEFAULT_MAX_CHARS_PER_SOURCE,
    DEFAULT_SUMMARIZER_MAX_OUTPUT_TOKENS,
    DEFAULT_SUMMARIZER_MAX_RETRIES,
    DEFAULT_SUMMARIZER_TIMEOUT_SECONDS,
    load,
)


def _write_config(tmp_path: Path, payload: dict[str, object]) -> Path:
    path = tmp_path / "config.json"
    path.write_text(json.dumps(payload), encoding="utf-8")
    return path


def test_load_reads_runtime_options(tmp_path: Path) -> None:
    path = _write_config(
        tmp_path,
        {
            "outputs": ["docs/models/models.catalog.md"],
            "max_chars_per_source": 123,
            "llm": {
                "model": "primary-model",
                "api_base_url": "https://llm.example.com/v1",
                "timeout_seconds": 45,
                "max_retries": 4,
                "max_output_tokens": 999,
                "disable_thinking": False,
            },
            "summarizer": {
                "enabled": True,
                "model": "summary-model",
                "api_base_url": "https://example.com/v1",
                "timeout_seconds": 33,
                "max_retries": 5,
                "max_output_tokens": 777,
                "disable_thinking": False,
            },
            "logging": {
                "capture_sources": True,
                "capture_prompts": True,
                "capture_llm_io": True,
                "capture_outputs": True,
            },
            "sources": [{"name": "api", "type": "text", "value": "seed"}],
        },
    )

    _, _, runtime = load(path)

    assert runtime.max_chars_per_source == 123
    assert runtime.llm.model == "primary-model"
    assert runtime.llm.api_base_url == "https://llm.example.com/v1"
    assert runtime.llm.timeout_seconds == 45
    assert runtime.llm.max_retries == 4
    assert runtime.llm.max_output_tokens == 999
    assert runtime.llm.disable_thinking is False
    assert runtime.summarizer.enabled is True
    assert runtime.summarizer.model == "summary-model"
    assert runtime.summarizer.api_base_url == "https://example.com/v1"
    assert runtime.summarizer.timeout_seconds == 33
    assert runtime.summarizer.max_retries == 5
    assert runtime.summarizer.max_output_tokens == 777
    assert runtime.summarizer.disable_thinking is False
    assert runtime.logging.capture_sources is True
    assert runtime.logging.capture_prompts is True
    assert runtime.logging.capture_llm_io is True
    assert runtime.logging.capture_outputs is True


def test_load_applies_runtime_defaults_when_omitted(tmp_path: Path) -> None:
    path = _write_config(
        tmp_path,
        {
            "outputs": ["docs/models/custom-a.md"],
            "sources": [{"name": "seed", "type": "text", "value": "ok"}],
        },
    )

    _, _, runtime = load(path)

    assert runtime.max_chars_per_source == DEFAULT_MAX_CHARS_PER_SOURCE
    assert runtime.llm.model == DEFAULT_LLM_MODEL
    assert runtime.llm.api_base_url == DEFAULT_LLM_API_BASE_URL
    assert runtime.llm.timeout_seconds == DEFAULT_LLM_TIMEOUT_SECONDS
    assert runtime.llm.max_retries == DEFAULT_LLM_MAX_RETRIES
    assert runtime.llm.max_output_tokens == DEFAULT_LLM_MAX_OUTPUT_TOKENS
    assert runtime.summarizer.model == DEFAULT_LLM_MODEL
    assert runtime.summarizer.api_base_url == DEFAULT_LLM_API_BASE_URL
    assert runtime.summarizer.timeout_seconds == DEFAULT_SUMMARIZER_TIMEOUT_SECONDS
    assert runtime.summarizer.max_retries == DEFAULT_SUMMARIZER_MAX_RETRIES
    assert runtime.summarizer.max_output_tokens == DEFAULT_SUMMARIZER_MAX_OUTPUT_TOKENS
