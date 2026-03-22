from __future__ import annotations

from models_pipeline.sources.base import SourceParser
from models_pipeline.sources.parsers import (
    FileSourceParser,
    ModelsDevApiSourceParser,
    TextSourceParser,
    UrlSourceParser,
)


class SourceParserRegistry:
    def __init__(self) -> None:
        self._parsers: dict[str, SourceParser] = {}

    def register(self, parser: SourceParser) -> None:
        kind = parser.supported_kind
        if kind in self._parsers:
            raise ValueError(f"parser for source type {kind!r} already registered")
        self._parsers[kind] = parser

    def get(self, kind: str) -> SourceParser:
        parser = self._parsers.get(kind)
        if parser is None:
            raise ValueError(
                f"unsupported source type: {kind!r}. Expected one of: {sorted(self.supported_kinds())}"
            )
        return parser

    def supported_kinds(self) -> tuple[str, ...]:
        return tuple(sorted(self._parsers.keys()))

    def kinds_requiring_crawl(self) -> set[str]:
        return {
            parser.supported_kind
            for parser in self._parsers.values()
            if parser.requires_crawl_support
        }


def build_default_registry() -> SourceParserRegistry:
    registry = SourceParserRegistry()
    registry.register(FileSourceParser())
    registry.register(UrlSourceParser())
    registry.register(TextSourceParser())
    registry.register(ModelsDevApiSourceParser())
    return registry


_DEFAULT_REGISTRY = build_default_registry()


def get_source_registry() -> SourceParserRegistry:
    return _DEFAULT_REGISTRY
