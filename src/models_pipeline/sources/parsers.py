from __future__ import annotations

import json
from pathlib import Path

from toon import encode as toon_encode

from models_pipeline import crawl
from models_pipeline.config.schema import SourceItem
from models_pipeline.sources.base import SourceParser
from models_pipeline.sources.http import fetch_models_dev_catalog


def _require_string_value(item: SourceItem, *, source_kind: str) -> str:
    if not isinstance(item.value, str):
        raise ValueError(f"{source_kind} source expects string value: {item.name!r}")
    return item.value


class FileSourceParser(SourceParser):
    @property
    def supported_kind(self) -> str:
        return "file"

    def validate(self, item: SourceItem) -> None:
        _require_string_value(item, source_kind=self.supported_kind)

    def parse(
        self, item: SourceItem, *, root: Path, debug_dir: Path | None = None
    ) -> str:
        del debug_dir
        target = (
            root / _require_string_value(item, source_kind=self.supported_kind)
        ).resolve()
        if root not in target.parents and target != root:
            raise ValueError(f"file source escapes workspace: {item.value!r}")
        return target.read_text(encoding="utf-8")


class UrlSourceParser(SourceParser):
    @property
    def supported_kind(self) -> str:
        return "url"

    @property
    def requires_crawl_support(self) -> bool:
        return True

    def validate(self, item: SourceItem) -> None:
        value = _require_string_value(item, source_kind=self.supported_kind)
        if not value.startswith(("http://", "https://")):
            raise ValueError(
                f"url source {item.name!r} value must start with 'http://' or 'https://'"
            )

    def parse(
        self, item: SourceItem, *, root: Path, debug_dir: Path | None = None
    ) -> str:
        del root
        return crawl.fetch(
            item.value,
            browser_settings=item.browser,
            run_settings=item.run,
            timeout_seconds=120,
            debug_dir=debug_dir,
        )


class TextSourceParser(SourceParser):
    @property
    def supported_kind(self) -> str:
        return "text"

    def validate(self, item: SourceItem) -> None:
        _require_string_value(item, source_kind=self.supported_kind)

    def parse(
        self, item: SourceItem, *, root: Path, debug_dir: Path | None = None
    ) -> str:
        del debug_dir
        del root
        return _require_string_value(item, source_kind=self.supported_kind)


class ModelsDevApiSourceParser(SourceParser):
    @property
    def supported_kind(self) -> str:
        return "models_dev_api"

    def validate(self, item: SourceItem) -> None:
        _require_string_value(item, source_kind=self.supported_kind)

    def parse(
        self, item: SourceItem, *, root: Path, debug_dir: Path | None = None
    ) -> str:
        del debug_dir
        del root
        providers: list[str] | None = (
            None
            if item.value == "default"
            else [part.strip() for part in item.value.split(",") if part.strip()]
        )
        text = fetch_models_dev_catalog(providers=providers)
        if item.to_toon:
            text = toon_encode(json.loads(text))
        return text
