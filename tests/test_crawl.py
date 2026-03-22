from types import SimpleNamespace

import pytest
from models_pipeline.crawl import ensure_available
from models_pipeline.crawl.markdown_extract import extract_markdown


def test_ensure_available_raises_when_crawl4ai_missing(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr("importlib.util.find_spec", lambda _name: None)
    with pytest.raises(RuntimeError, match="crawl4ai is required"):
        ensure_available()


def test_extract_markdown_uses_raw_html() -> None:
    result = SimpleNamespace(
        html="<p>raw html</p>",
    )

    extracted = extract_markdown(result, "https://example.com")

    assert extracted == "raw html"


def test_extract_markdown_raises_when_raw_html_missing() -> None:
    result = SimpleNamespace(html="")
    with pytest.raises(RuntimeError, match="empty raw HTML content"):
        extract_markdown(result, "https://example.com")


def test_extract_markdown_converts_raw_html_with_svg_aria_label() -> None:
    result = SimpleNamespace(
        html=(
            "<table><tr><td><svg\n"
            'aria-label="Works"\n'
            "viewBox='0 0 16 16'>\n"
            "<path></path>\n"
            "</svg></td></tr></table>"
        ),
    )

    extracted = extract_markdown(result, "https://example.com")

    assert "Works" in extracted
    assert "<svg" not in extracted


def test_extract_markdown_replaces_svg_tokens_in_raw_html() -> None:
    result = SimpleNamespace(
        html=(
            "<svg aria-label='Includes models'></svg> "
            "<svg class='foo octicon-check bar'></svg>"
        ),
    )

    extracted = extract_markdown(result, "https://example.com")

    assert "Includes models" in extracted
    assert "<svg" not in extracted
