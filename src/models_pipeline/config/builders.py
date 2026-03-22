from typing import cast

from models_pipeline.config.parsers import (
    parse_bool,
    parse_config_object,
    parse_int,
    parse_object,
    parse_optional_bool,
)
from models_pipeline.config.schema import (
    DEFAULT_LLM_API_BASE_URL,
    DEFAULT_LLM_DISABLE_THINKING,
    DEFAULT_LLM_MAX_OUTPUT_TOKENS,
    DEFAULT_LLM_MAX_RETRIES,
    DEFAULT_LLM_MODEL,
    DEFAULT_LLM_TIMEOUT_SECONDS,
    DEFAULT_MAX_CHARS_PER_SOURCE,
    DEFAULT_SUMMARIZE_SOURCES_WITH_LLM,
    DEFAULT_SUMMARIZER_API_BASE_URL,
    DEFAULT_SUMMARIZER_DISABLE_THINKING,
    DEFAULT_SUMMARIZER_MAX_OUTPUT_TOKENS,
    DEFAULT_SUMMARIZER_MAX_RETRIES,
    DEFAULT_SUMMARIZER_MODEL,
    DEFAULT_SUMMARIZER_TIMEOUT_SECONDS,
    LLMConfig,
    LoggingConfig,
    PipelineConfig,
    SourceItem,
    SummarizerConfig,
)
from models_pipeline.config.validators import (
    parse_models_dev_api_to_toon,
    parse_source_value,
)


def build_runtime_config(payload: dict[str, object]) -> PipelineConfig:
    return PipelineConfig(
        max_chars_per_source=parse_int(
            payload, "max_chars_per_source", DEFAULT_MAX_CHARS_PER_SOURCE
        ),
        llm=_build_llm_config(payload),
        summarizer=_build_summarizer_config(payload),
        logging=_build_logging_config(payload),
    )


def build_source_item(
    item: dict[str, object], supported_kinds: tuple[str, ...] | list[str]
) -> SourceItem:
    name = _parse_source_name(item)
    kind = _parse_source_kind(item, name, supported_kinds)
    _validate_source_item(item, name)
    return SourceItem(
        name=name,
        kind=kind,
        value=parse_source_value(item, name, kind),
        summarize=parse_optional_bool(item, "summarize"),
        browser=parse_config_object(item, name, "browser"),
        run=parse_config_object(item, name, "run"),
        to_toon=parse_models_dev_api_to_toon(item, name, kind),
    )


def coerce_source_item(item: object) -> dict[str, object]:
    if not isinstance(item, dict):
        raise ValueError("each source must be an object")
    return cast(dict[str, object], item)


def _build_llm_config(payload: dict[str, object]) -> LLMConfig:
    llm = parse_object(payload, "llm")
    return LLMConfig(
        model=_parse_stripped_string(llm, "model", DEFAULT_LLM_MODEL)
        or DEFAULT_LLM_MODEL,
        api_base_url=_parse_stripped_string(
            llm, "api_base_url", DEFAULT_LLM_API_BASE_URL
        )
        or DEFAULT_LLM_API_BASE_URL,
        timeout_seconds=parse_int(llm, "timeout_seconds", DEFAULT_LLM_TIMEOUT_SECONDS),
        max_retries=parse_int(llm, "max_retries", DEFAULT_LLM_MAX_RETRIES),
        max_output_tokens=parse_int(
            llm, "max_output_tokens", DEFAULT_LLM_MAX_OUTPUT_TOKENS
        ),
        disable_thinking=parse_bool(
            llm, "disable_thinking", DEFAULT_LLM_DISABLE_THINKING
        ),
    )


def _build_summarizer_config(payload: dict[str, object]) -> SummarizerConfig:
    summarizer = parse_object(payload, "summarizer")
    return SummarizerConfig(
        enabled=parse_bool(summarizer, "enabled", DEFAULT_SUMMARIZE_SOURCES_WITH_LLM),
        model=_parse_stripped_string(summarizer, "model", DEFAULT_SUMMARIZER_MODEL),
        api_base_url=_parse_stripped_string(
            summarizer, "api_base_url", DEFAULT_SUMMARIZER_API_BASE_URL
        ),
        timeout_seconds=parse_int(
            summarizer, "timeout_seconds", DEFAULT_SUMMARIZER_TIMEOUT_SECONDS
        ),
        max_retries=parse_int(
            summarizer, "max_retries", DEFAULT_SUMMARIZER_MAX_RETRIES
        ),
        max_output_tokens=parse_int(
            summarizer, "max_output_tokens", DEFAULT_SUMMARIZER_MAX_OUTPUT_TOKENS
        ),
        disable_thinking=parse_bool(
            summarizer, "disable_thinking", DEFAULT_SUMMARIZER_DISABLE_THINKING
        ),
    )


def _build_logging_config(payload: dict[str, object]) -> LoggingConfig:
    logging = parse_object(payload, "logging")
    return LoggingConfig(
        capture_sources=parse_bool(logging, "capture_sources", False),
        capture_prompts=parse_bool(logging, "capture_prompts", False),
        capture_llm_io=parse_bool(logging, "capture_llm_io", False),
        capture_outputs=parse_bool(logging, "capture_outputs", False),
    )


def _parse_stripped_string(payload: dict[str, object], key: str, default: str) -> str:
    return str(payload.get(key, default)).strip()


def _parse_source_name(item: dict[str, object]) -> str:
    name = _parse_stripped_string(item, "name", "")
    if not name:
        raise ValueError("source name must be a non-empty string")
    return name


def _parse_source_kind(
    item: dict[str, object],
    source_name: str,
    supported_kinds: tuple[str, ...] | list[str],
) -> str:
    kind = _parse_stripped_string(item, "type", "")
    if kind not in supported_kinds:
        raise ValueError(
            f"source '{source_name}' has unsupported type {kind!r}; expected one of {list(supported_kinds)}"
        )
    return kind


def _validate_source_item(item: dict[str, object], source_name: str) -> None:
    if "markdown" in item:
        raise ValueError(
            f"source '{source_name}' does not support 'markdown'; markdown is always derived from raw HTML"
        )
    if "urls" in item:
        raise ValueError(
            f"source '{source_name}' does not support 'urls'; use a single URL in 'value'"
        )
