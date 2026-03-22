import json
from pathlib import Path
from typing import cast

from crawl4ai import AsyncWebCrawler
from crawl4ai.models import CrawlResult, CrawlResultContainer

from models_pipeline.crawl.config_core import build_browser_config, build_run_config
from models_pipeline.crawl.markdown_extract import extract_markdown


def _to_text(value: object) -> str:
    return value if isinstance(value, str) else ""


def _extract_tables(result: CrawlResult) -> list[dict[str, object]]:
    raw_tables = result.tables
    normalized: list[dict[str, object]] = []
    for table in raw_tables:
        headers = table.get("headers", [])
        rows = table.get("rows", [])
        caption = table.get("caption", "")
        summary = table.get("summary", "")
        normalized.append(
            {
                "headers": headers if isinstance(headers, list) else [],
                "rows": rows if isinstance(rows, list) else [],
                "caption": caption if isinstance(caption, str) else "",
                "summary": summary if isinstance(summary, str) else "",
            }
        )
    return normalized


def _build_debug_sections(entries: list[dict[str, object]], field: str) -> str:
    if len(entries) == 1:
        return _to_text(entries[0].get(field, ""))
    chunks: list[str] = []
    for entry in entries:
        url = _to_text(entry.get("url", ""))
        body = _to_text(entry.get(field, ""))
        chunks.append(f"<!-- {url} -->\n{body}")
    return "\n\n".join(chunks)


def _write_crawl_debug(
    debug_dir: Path,
    entries: list[dict[str, object]],
) -> None:
    debug_dir.mkdir(parents=True, exist_ok=True)
    (debug_dir / "raw_html.txt").write_text(
        _build_debug_sections(entries, "raw_html"), encoding="utf-8"
    )
    (debug_dir / "cleaned_html.txt").write_text(
        _build_debug_sections(entries, "cleaned_html"), encoding="utf-8"
    )
    tables: list[dict[str, object]] = []
    for entry in entries:
        entry_tables = entry.get("tables", [])
        if isinstance(entry_tables, list):
            tables.extend(cast(list[dict[str, object]], entry_tables))
    (debug_dir / "tables.json").write_text(
        json.dumps(tables, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


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
            _write_crawl_debug(
                debug_dir,
                [
                    {
                        "url": url,
                        "raw_html": _to_text(result.html),
                        "cleaned_html": _to_text(
                            result.cleaned_html
                            if result.cleaned_html is not None
                            else ""
                        ),
                        "tables": _extract_tables(result),
                    }
                ],
            )
        extracted = extract_markdown(result, url)
        return extracted
