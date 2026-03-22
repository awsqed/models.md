from typing import cast


def parse_bool(payload: dict[str, object], key: str, default: bool) -> bool:
    raw = payload.get(key, default)
    if isinstance(raw, bool):
        return raw
    raise ValueError(f"{key} must be a boolean")


def parse_int(payload: dict[str, object], key: str, default: int) -> int:
    raw = payload.get(key, default)
    if isinstance(raw, bool) or not isinstance(raw, int):
        raise ValueError(f"{key} must be an integer")
    return raw


def parse_object(payload: dict[str, object], key: str) -> dict[str, object]:
    raw = payload.get(key, {})
    if raw is None:
        raw = {}
    if not isinstance(raw, dict):
        raise ValueError(f"{key} must be an object")
    return cast(dict[str, object], raw)


def parse_optional_bool(payload: dict[str, object], key: str) -> bool | None:
    if key not in payload:
        return None
    raw = payload.get(key)
    if isinstance(raw, bool):
        return raw
    raise ValueError(f"{key} must be a boolean")


def parse_config_object(
    item: dict[str, object], source_name: str, key: str
) -> dict[str, object]:
    if key not in item:
        return {}
    raw = item.get(key, {})
    if raw is None:
        raw = {}
    if not isinstance(raw, dict):
        raise ValueError(f"source '{source_name}' {key} config must be an object")
    raw_dict = cast(dict[object, object], raw)
    return {str(k): v for k, v in raw_dict.items()}
