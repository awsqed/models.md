from pathlib import Path

from models_pipeline.config.schema import SourceItem
from models_pipeline.sources.base import SourceParser
from models_pipeline.sources.parsers.shared import require_string_value


class FileSourceParser(SourceParser):
    @property
    def supported_kind(self) -> str:
        return "file"

    def validate(self, item: SourceItem) -> None:
        require_string_value(item, source_kind=self.supported_kind)

    def parse(
        self, item: SourceItem, *, root: Path, debug_dir: Path | None = None
    ) -> str:
        del debug_dir
        target = (
            root / require_string_value(item, source_kind=self.supported_kind)
        ).resolve()
        if root not in target.parents and target != root:
            raise ValueError(f"file source escapes workspace: {item.value!r}")
        return target.read_text(encoding="utf-8")
