from typing import cast

from models_pipeline.config.parsers import parse_config_object, parse_optional_bool
from models_pipeline.config.schema import SourceItem
from models_pipeline.config.validators import (
    parse_models_dev_api_to_toon,
    parse_source_value,
)


def build_source_item(
    item: dict[str, object], supported_kinds: tuple[str, ...] | list[str]
) -> SourceItem:
    name = _parse_source_name(item)
    kind = _parse_source_kind(item, name, supported_kinds)
    _validate_source_item(item, name)
    return SourceItem(
        name=name,
        kind=kind,
        value=parse_source_value(item, name, kind),
        summarize=parse_optional_bool(item, "summarize"),
        browser=parse_config_object(item, name, "browser"),
        run=parse_config_object(item, name, "run"),
        to_toon=parse_models_dev_api_to_toon(item, name, kind),
    )


def coerce_source_item(item: object) -> dict[str, object]:
    if not isinstance(item, dict):
        raise ValueError("each source must be an object")
    return cast(dict[str, object], item)


def _parse_stripped_string(payload: dict[str, object], key: str, default: str) -> str:
    return str(payload.get(key, default)).strip()


def _parse_source_name(item: dict[str, object]) -> str:
    name = _parse_stripped_string(item, "name", "")
    if not name:
        raise ValueError("source name must be a non-empty string")
    return name


def _parse_source_kind(
    item: dict[str, object],
    source_name: str,
    supported_kinds: tuple[str, ...] | list[str],
) -> str:
    kind = _parse_stripped_string(item, "type", "")
    if kind not in supported_kinds:
        raise ValueError(
            f"source '{source_name}' has unsupported type {kind!r}; expected one of {list(supported_kinds)}"
        )
    return kind


def _validate_source_item(item: dict[str, object], source_name: str) -> None:
    if "markdown" in item:
        raise ValueError(
            f"source '{source_name}' does not support 'markdown'; markdown is always derived from raw HTML"
        )
    if "urls" in item:
        raise ValueError(
            f"source '{source_name}' does not support 'urls'; use a single URL in 'value'"
        )
