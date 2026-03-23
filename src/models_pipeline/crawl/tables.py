from crawl4ai.models import CrawlResult


def extract_tables(result: CrawlResult) -> list[dict[str, object]]:
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
