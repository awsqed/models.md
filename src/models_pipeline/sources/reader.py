"""Read individual pipeline sources."""

from collections.abc import Callable
from pathlib import Path

from models_pipeline.config.schema import DEFAULT_MAX_CHARS_PER_SOURCE, SourceItem
from models_pipeline.sources.registry import get_source_registry

Summarizer = Callable[[str, str], str]


def read(
    item: SourceItem, *, root: Path, max_chars: int = DEFAULT_MAX_CHARS_PER_SOURCE
) -> str:
    """Return the raw text content for *item*, clipped to *max_chars*."""
    registry = get_source_registry()
    parser = registry.get(item.kind)
    parser.validate(item)
    text = parser.parse(item, root=root)

    if len(text) > max_chars:
        text = text[:max_chars] + "\n...[truncated by pipeline]...\n"
    return text


def read_all(
    items: list[SourceItem],
    *,
    root: Path,
    max_chars: int = DEFAULT_MAX_CHARS_PER_SOURCE,
    summarizer: Summarizer | None = None,
    default_summarize: bool = False,
    crawl_debug_root: Path | None = None,
) -> list[tuple[str, str, bool]]:
    """Read every source and return (name, text, summarized) tuples with progress logs."""
    blobs: list[tuple[str, str, bool]] = []
    for item in items:
        print(
            f"[source] reading '{item.name}' (type={item.kind}) ...",
            end=" ",
            flush=True,
        )
        parser = get_source_registry().get(item.kind)
        debug_dir = (
            crawl_debug_root / item.name
            if item.kind == "url" and crawl_debug_root
            else None
        )
        parser.validate(item)
        text = parser.parse(item, root=root, debug_dir=debug_dir)
        if len(text) > max_chars:
            text = text[:max_chars] + "\n...[truncated by pipeline]...\n"
        should_summarize = item.summarize
        if should_summarize is None:
            should_summarize = default_summarize
        summarized = False
        if summarizer is not None and should_summarize:
            print("summarizing ...", end=" ", flush=True)
            text = summarizer(item.name, text)
            summarized = True
        if debug_dir is not None:
            debug_dir.mkdir(parents=True, exist_ok=True)
            (debug_dir / "final.txt").write_text(text, encoding="utf-8")
        truncated = len(text) >= max_chars
        print(f"{len(text)} chars{'  [TRUNCATED]' if truncated else ''}")
        blobs.append((item.name, text, summarized))
    return blobs
