from pathlib import Path

from models_pipeline.config.schema import SourceItem
from models_pipeline.sources.base import SourceParser
from models_pipeline.sources.parsers.shared import require_string_value


class TextSourceParser(SourceParser):
    @property
    def supported_kind(self) -> str:
        return "text"

    def validate(self, item: SourceItem) -> None:
        require_string_value(item, source_kind=self.supported_kind)

    def parse(
        self, item: SourceItem, *, root: Path, debug_dir: Path | None = None
    ) -> str:
        del debug_dir
        del root
        return require_string_value(item, source_kind=self.supported_kind)
