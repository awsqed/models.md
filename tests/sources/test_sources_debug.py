import json
from pathlib import Path

from models_pipeline.crawl.fetch_workers import _write_crawl_debug


def test_write_crawl_debug_writes_requested_debug_artifacts(tmp_path: Path) -> None:
    debug_dir = tmp_path / "crawl_debug" / "url"
    _write_crawl_debug(
        debug_dir,
        [
            {
                "url": "https://example.com",
                "raw_html": "<html>x</html>",
                "cleaned_html": "",
                "tables": [
                    {
                        "headers": ["h"],
                        "rows": [["r"]],
                        "caption": "c",
                        "summary": "s",
                    }
                ],
            }
        ],
    )

    assert (debug_dir / "raw_html.txt").read_text("utf-8") == "<html>x</html>"
    assert (debug_dir / "cleaned_html.txt").read_text("utf-8") == ""
    assert json.loads((debug_dir / "tables.json").read_text("utf-8")) == [
        {"headers": ["h"], "rows": [["r"]], "caption": "c", "summary": "s"}
    ]
