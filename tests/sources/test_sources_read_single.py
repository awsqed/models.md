from pathlib import Path

import pytest
from models_pipeline.config import SourceItem
from models_pipeline.sources import read


def test_read_models_dev_api_source(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(
        "models_pipeline.sources.parsers.fetch_models_dev_catalog",
        lambda providers=None: '[{"provider_id": "github-copilot"}]\n',
    )
    item = SourceItem(name="api", kind="models_dev_api", value="github-copilot")

    text = read(item, root=Path("/tmp"))

    assert "github-copilot" in text


def test_read_models_dev_api_source_to_toon(monkeypatch: pytest.MonkeyPatch) -> None:
    raw_json = '[{"provider_id":"github-copilot","models":[{"id":"gpt-5"}]}]'
    monkeypatch.setattr(
        "models_pipeline.sources.parsers.fetch_models_dev_catalog",
        lambda providers=None: raw_json,
    )
    item = SourceItem(
        name="api", kind="models_dev_api", value="github-copilot", to_toon=True
    )

    text = read(item, root=Path("/tmp"))

    assert "provider_id" in text
    assert "github-copilot" in text
    assert "models" in text
    assert "id" in text
    assert text != raw_json
    assert '"provider_id"' not in text


def test_read_models_dev_api_source_to_toon_invalid_json(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        "models_pipeline.sources.parsers.fetch_models_dev_catalog",
        lambda providers=None: "{invalid json}",
    )
    item = SourceItem(
        name="api", kind="models_dev_api", value="github-copilot", to_toon=True
    )

    with pytest.raises(ValueError):
        read(item, root=Path("/tmp"))


def test_read_rejects_escaping_file_source(tmp_path: Path) -> None:
    outside = tmp_path.parent / "outside.txt"
    outside.write_text("secret", encoding="utf-8")
    item = SourceItem(name="file", kind="file", value=f"../{outside.name}")

    with pytest.raises(ValueError, match="escapes workspace"):
        read(item, root=tmp_path)


def test_read_truncates_long_text_source() -> None:
    item = SourceItem(name="text", kind="text", value="x" * 20)
    text = read(item, root=Path("/tmp"), max_chars=8)
    assert text.startswith("xxxxxxxx")
    assert text.endswith("\n...[truncated by pipeline]...\n")


def test_read_file_source(tmp_path: Path) -> None:
    (tmp_path / "seed.txt").write_text("hello", encoding="utf-8")
    item = SourceItem(name="file", kind="file", value="seed.txt")
    assert read(item, root=tmp_path) == "hello"


def test_read_url_single_calls_fetch(monkeypatch: pytest.MonkeyPatch) -> None:
    called: dict[str, object] = {}

    def fake_fetch(url: str, **kwargs: object) -> str:
        called["url"] = url
        called["kwargs"] = kwargs
        return "body"

    monkeypatch.setattr("models_pipeline.sources.parsers.crawl.fetch", fake_fetch)
    item = SourceItem(name="u", kind="url", value="https://example.com")

    text = read(item, root=Path("/tmp"))

    assert text == "body"
    assert called["url"] == "https://example.com"
    assert isinstance(called["kwargs"], dict)
