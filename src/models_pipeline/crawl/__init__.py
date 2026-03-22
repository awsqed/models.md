import importlib.util

from models_pipeline.crawl.fetch_sync import fetch_with_timeout as fetch

__all__ = ["ensure_available", "fetch"]


def ensure_available() -> None:
    """Raise a clear error if crawl4ai is somehow not installed at runtime."""
    if importlib.util.find_spec("crawl4ai") is None:
        raise RuntimeError(
            "crawl4ai is required for URL sources. "
            "Install with: uv sync && uv run crawl4ai-setup"
        )
