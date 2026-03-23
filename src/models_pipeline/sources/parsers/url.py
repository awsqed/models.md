from pathlib import Path

from models_pipeline import crawl
from models_pipeline.config.schema import SourceItem
from models_pipeline.sources.base import SourceParser
from models_pipeline.sources.parsers.shared import require_string_value


class UrlSourceParser(SourceParser):
    @property
    def supported_kind(self) -> str:
        return "url"

    @property
    def requires_crawl_support(self) -> bool:
        return True

    def validate(self, item: SourceItem) -> None:
        value = require_string_value(item, source_kind=self.supported_kind)
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
