from typing import Any

from crawl4ai import BrowserConfig, CacheMode, CrawlerRunConfig


def build_browser_config(raw: dict[str, object]) -> BrowserConfig:
    kwargs: dict[str, Any] = {"verbose": False}
    if raw:
        kwargs.update(raw)
    return BrowserConfig(**kwargs)


def build_run_config(
    raw: dict[str, object],
) -> CrawlerRunConfig:
    kwargs: dict[str, Any] = {"cache_mode": CacheMode.BYPASS, "verbose": False}

    if raw:
        overrides = dict(raw)
        if "markdown_generator" in overrides:
            raise ValueError(
                "run.markdown_generator is not supported in JSON config. "
                "Crawl markdown generation is disabled; markdown is derived from raw HTML."
            )
        if "cache_mode" in overrides:
            cm = overrides["cache_mode"]
            if isinstance(cm, str):
                overrides["cache_mode"] = CacheMode[cm.upper()]
        kwargs.update(overrides)
    return CrawlerRunConfig(**kwargs)
