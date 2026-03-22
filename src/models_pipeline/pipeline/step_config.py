import os
from pathlib import Path

from models_pipeline import config, crawl
from models_pipeline.pipeline.types import LoadedConfig, PipelineOptions
from models_pipeline.sources.registry import get_source_registry


def source_config_dict(item: config.SourceItem) -> dict[str, object]:
    return {
        "name": item.name,
        "type": item.kind,
        "value": item.value,
        "summarize": item.summarize,
        "browser": item.browser,
        "run": item.run,
        "to_toon": item.to_toon,
    }


def _validate_source_items(source_items: list[config.SourceItem]) -> None:
    if not source_items:
        raise ValueError("config must define at least one source")
    names = [item.name for item in source_items]
    if len(names) != len(set(names)):
        raise ValueError("source names must be unique")
    registry = get_source_registry()
    for item in source_items:
        parser = registry.get(item.kind)
        parser.validate(item)


def step_load_config(options: PipelineOptions, root: Path) -> LoadedConfig:
    config_path = options.config_path.resolve()
    source_items, output_names, runtime_config = config.load(config_path)
    _validate_source_items(source_items)

    model = options.model_override.strip() or runtime_config.llm.model
    api_base_url = (
        options.api_base_url_override.strip() or runtime_config.llm.api_base_url
    )
    print(f"[config] model={model}  api_base_url={api_base_url}")
    print(
        f"[config] sources={len(source_items)}  "
        f"max_chars={runtime_config.max_chars_per_source}"
    )
    print(
        f"[config] llm_timeout={runtime_config.llm.timeout_seconds}s  "
        f"llm_retries={runtime_config.llm.max_retries}"
    )
    print(f"[config] llm_max_output_tokens={runtime_config.llm.max_output_tokens}")
    print(f"[config] llm_disable_thinking={runtime_config.llm.disable_thinking}")
    print(f"[config] summarize_sources_with_llm={runtime_config.summarizer.enabled}")
    print(
        "[config] openai_api_key_present="
        f"{bool(os.getenv('OPENAI_API_KEY', '').strip())}"
    )
    return LoadedConfig(
        path=config_path,
        model=model,
        api_base_url=api_base_url,
        source_items=source_items,
        output_names=output_names,
        runtime=runtime_config,
    )


def step_ensure_crawl(loaded: LoadedConfig) -> None:
    crawl_kinds = get_source_registry().kinds_requiring_crawl()
    has_crawl_sources = any(item.kind in crawl_kinds for item in loaded.source_items)
    if has_crawl_sources:
        crawl.ensure_available()
