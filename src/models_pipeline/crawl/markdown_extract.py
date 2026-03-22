import re

from crawl4ai import CrawlResult
from markdownify import markdownify

SVG_ARIA_LABEL_RE = re.compile(
    r"<svg\b(?=[^>]*\baria-label=(['\"])(.*?)\1)[^>]*>.*?</svg>",
    re.DOTALL,
)


def _trim_empty_newlines(text: str) -> str:
    return re.sub(r"\n{2,}", "\n", text.strip())


def _replace_svg_tokens(text: str) -> str:
    return SVG_ARIA_LABEL_RE.sub(lambda match: match.group(2), text)


def extract_markdown(result: CrawlResult, url: str) -> str:
    html = result.html
    if not html.strip():
        raise RuntimeError(f"crawl4ai returned empty raw HTML content for {url}")
    preprocessed = _trim_empty_newlines(html)
    preprocessed = _replace_svg_tokens(preprocessed)
    return markdownify(preprocessed, strip=["a"], heading_style="ATX")
