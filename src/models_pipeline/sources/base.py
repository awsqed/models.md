from __future__ import annotations

from abc import ABC, abstractmethod
from pathlib import Path

from models_pipeline.config.schema import SourceItem


class SourceParser(ABC):
    @property
    @abstractmethod
    def supported_kind(self) -> str:
        """Return the source kind this parser handles."""

    def validate(self, item: SourceItem) -> None:
        """Validate source configuration before parse."""

    @abstractmethod
    def parse(
        self, item: SourceItem, *, root: Path, debug_dir: Path | None = None
    ) -> str:
        """Return untruncated text for one source item."""

    @property
    def requires_crawl_support(self) -> bool:
        """Signal whether this parser depends on crawl runtime setup."""
        return False
