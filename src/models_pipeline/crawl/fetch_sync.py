import asyncio
from pathlib import Path

from models_pipeline.crawl.fetch_workers import single_page


def fetch_with_timeout(
    url: str,
    *,
    browser_settings: dict[str, object] | None = None,
    run_settings: dict[str, object] | None = None,
    timeout_seconds: int = 120,
    debug_dir: Path | None = None,
) -> str:
    browser_raw = browser_settings or {}
    run_raw = run_settings or {}

    coro = single_page(url, browser_raw, run_raw, debug_dir=debug_dir)

    try:
        return asyncio.run(asyncio.wait_for(coro, timeout=timeout_seconds))
    except TimeoutError as exc:
        raise RuntimeError(
            f"crawl4ai timed out after {timeout_seconds}s for {url}"
        ) from exc
