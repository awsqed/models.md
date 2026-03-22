import json
from pathlib import Path

from models_pipeline.config import SourceItem
from models_pipeline.sources import read_all


def test_read_url_single_writes_crawl_debug_files(monkeypatch, tmp_path: Path) -> None:
    def fake_fetch(url: str, **kwargs: object) -> str:
        debug_dir = kwargs.get("debug_dir")
        assert debug_dir == tmp_path / "crawl_debug" / "u"
        assert isinstance(debug_dir, Path)
        debug_dir.mkdir(parents=True, exist_ok=True)
        (debug_dir / "raw_html.txt").write_text("<html>raw</html>", encoding="utf-8")
        (debug_dir / "cleaned_html.txt").write_text("<p>clean</p>", encoding="utf-8")
        (debug_dir / "tables.json").write_text(
            json.dumps(
                [
                    {
                        "headers": ["h1"],
                        "rows": [["r1"]],
                        "caption": "cap",
                        "summary": "sum",
                    }
                ]
            )
            + "\n",
            encoding="utf-8",
        )
        return "final body"

    monkeypatch.setattr("models_pipeline.sources.parsers.crawl.fetch", fake_fetch)
    item = SourceItem(name="u", kind="url", value="https://example.com")

    blobs = read_all(
        [item], root=Path("/tmp"), crawl_debug_root=tmp_path / "crawl_debug"
    )

    assert blobs == [("u", "final body", False)]
    debug_dir = tmp_path / "crawl_debug" / "u"
    assert (debug_dir / "raw_html.txt").read_text("utf-8") == "<html>raw</html>"
    assert (debug_dir / "cleaned_html.txt").read_text("utf-8") == "<p>clean</p>"
    assert json.loads((debug_dir / "tables.json").read_text("utf-8")) == [
        {"headers": ["h1"], "rows": [["r1"]], "caption": "cap", "summary": "sum"}
    ]
    assert (debug_dir / "final.txt").read_text("utf-8") == "final body"


def test_read_all_url_without_debug_root_does_not_write_debug_files(
    monkeypatch, tmp_path: Path
) -> None:
    def fake_fetch(url: str, **kwargs: object) -> str:
        assert kwargs.get("debug_dir") is None
        return "body"

    monkeypatch.setattr("models_pipeline.sources.parsers.crawl.fetch", fake_fetch)
    item = SourceItem(name="u", kind="url", value="https://example.com")

    blobs = read_all([item], root=Path("/tmp"))

    assert blobs == [("u", "body", False)]
    assert not any(tmp_path.iterdir())


def test_read_all_can_summarize_with_llm(tmp_path: Path) -> None:
    item = SourceItem(
        name="notes",
        kind="text",
        value="Provider: github-copilot\nModel: glm-5",
        summarize=True,
    )

    def summarizer(_source_name: str, _text: str) -> str:
        return "summarized source"

    blobs = read_all(
        [item],
        root=tmp_path,
        summarizer=summarizer,
    )

    assert blobs == [("notes", "summarized source", True)]


def test_read_all_uses_default_summarize_when_unspecified(tmp_path: Path) -> None:
    item = SourceItem(name="notes", kind="text", value="raw")

    def summarizer(_source_name: str, _text: str) -> str:
        return "summarized"

    blobs = read_all(
        [item], root=tmp_path, summarizer=summarizer, default_summarize=True
    )

    assert blobs == [("notes", "summarized", True)]


def test_read_all_source_summarize_false_overrides_default(tmp_path: Path) -> None:
    item = SourceItem(name="notes", kind="text", value="raw", summarize=False)

    def summarizer(_source_name: str, _text: str) -> str:
        return "summarized"

    blobs = read_all(
        [item], root=tmp_path, summarizer=summarizer, default_summarize=True
    )

    assert blobs == [("notes", "raw", False)]
