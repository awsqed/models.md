import json
from pathlib import Path
from typing import cast


def to_text(value: object) -> str:
    return value if isinstance(value, str) else ""


def build_debug_sections(entries: list[dict[str, object]], field: str) -> str:
    if len(entries) == 1:
        return to_text(entries[0].get(field, ""))
    chunks: list[str] = []
    for entry in entries:
        url = to_text(entry.get("url", ""))
        body = to_text(entry.get(field, ""))
        chunks.append(f"<!-- {url} -->\n{body}")
    return "\n\n".join(chunks)


def write_crawl_debug(
    debug_dir: Path,
    entries: list[dict[str, object]],
) -> None:
    debug_dir.mkdir(parents=True, exist_ok=True)
    (debug_dir / "raw_html.txt").write_text(
        build_debug_sections(entries, "raw_html"), encoding="utf-8"
    )
    (debug_dir / "cleaned_html.txt").write_text(
        build_debug_sections(entries, "cleaned_html"), encoding="utf-8"
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
