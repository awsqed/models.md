from pathlib import Path

from crawl4ai import AsyncWebCrawler
from crawl4ai.models import CrawlResult, CrawlResultContainer

from models_pipeline.crawl.config_core import build_browser_config, build_run_config
from models_pipeline.crawl.debug_dump import to_text, write_crawl_debug
from models_pipeline.crawl.markdown_extract import extract_markdown
from models_pipeline.crawl.tables import extract_tables


async def single_page(
    url: str,
    browser_raw: dict[str, object],
    run_raw: dict[str, object],
    debug_dir: Path | None = None,
) -> str:
    browser_cfg = build_browser_config(browser_raw)
    run_cfg = build_run_config(run_raw)
    async with AsyncWebCrawler(config=browser_cfg) as crawler:
        result_container = await crawler.arun(url=url, config=run_cfg)
        if not isinstance(result_container, CrawlResultContainer):
            raise RuntimeError(
                f"unexpected crawl4ai result type: {type(result_container)}"
            )
        result = result_container._results[0] if result_container._results else None
        if not isinstance(result, CrawlResult):
            raise RuntimeError(f"unexpected crawl4ai result type: {type(result)}")
        if not result.success:
            detail = (
                result.error_message
                if result.error_message is not None
                else "unknown crawl error"
            )
            raise RuntimeError(f"crawl4ai failed for {url}: {detail}")
        if debug_dir is not None:
            write_crawl_debug(
                debug_dir,
                [
                    {
                        "url": url,
                        "raw_html": to_text(result.html),
                        "cleaned_html": to_text(
                            result.cleaned_html
                            if result.cleaned_html is not None
                            else ""
                        ),
                        "tables": extract_tables(result),
                    }
                ],
            )
        extracted = extract_markdown(result, url)
        return extracted
