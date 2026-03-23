import json
from pathlib import Path

from toon import encode as toon_encode

from models_pipeline.config.schema import SourceItem
from models_pipeline.sources.base import SourceParser
from models_pipeline.sources.http import fetch_models_dev_catalog
from models_pipeline.sources.parsers.shared import require_string_value


class ModelsDevApiSourceParser(SourceParser):
    @property
    def supported_kind(self) -> str:
        return "models_dev_api"

    def validate(self, item: SourceItem) -> None:
        require_string_value(item, source_kind=self.supported_kind)

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
