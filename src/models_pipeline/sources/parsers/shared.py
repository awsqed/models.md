from models_pipeline.config.schema import SourceItem


def require_string_value(item: SourceItem, *, source_kind: str) -> str:
    if not isinstance(item.value, str):
        raise ValueError(f"{source_kind} source expects string value: {item.name!r}")
    return item.value
