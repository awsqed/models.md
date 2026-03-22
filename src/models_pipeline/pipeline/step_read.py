from pathlib import Path

from models_pipeline import sources
from models_pipeline.pipeline.types import LoadedConfig
from models_pipeline.sources import Summarizer


def step_load_schema(schema_path: Path) -> str:
    schema_text = schema_path.read_text(encoding="utf-8")
    print(f"[schema] {len(schema_text)} chars from {schema_path.name}")
    return schema_text


def step_read_sources(
    loaded: LoadedConfig,
    root: Path,
    summarizer: Summarizer | None = None,
    crawl_debug_root: Path | None = None,
) -> list[tuple[str, str, bool]]:
    return sources.read_all(
        loaded.source_items,
        root=root,
        max_chars=loaded.runtime.max_chars_per_source,
        summarizer=summarizer,
        default_summarize=loaded.runtime.summarizer.enabled,
        crawl_debug_root=crawl_debug_root,
    )
