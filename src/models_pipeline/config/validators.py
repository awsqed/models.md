def validate_output_name(name: str) -> None:
    if not name.startswith("docs/models/") or not name.endswith(".md"):
        raise ValueError(
            "output paths must start with 'docs/models/' and end with '.md'"
        )


def parse_models_dev_api_to_toon(
    payload: dict[str, object], source_name: str, kind: str
) -> bool:
    if "to_toon" not in payload:
        return False
    raw = payload.get("to_toon")
    if not isinstance(raw, bool):
        raise ValueError(f"source '{source_name}' to_toon must be a boolean")
    if kind != "models_dev_api":
        raise ValueError(
            f"source '{source_name}' to_toon is only supported for models_dev_api sources"
        )
    return raw


def parse_source_value(item: dict[str, object], source_name: str, kind: str) -> str:
    has_value = "value" in item
    has_urls = "urls" in item
    if has_value and has_urls:
        raise ValueError(
            f"source '{source_name}' cannot define both 'value' and 'urls'"
        )

    if has_urls:
        raise ValueError(
            f"source '{source_name}' does not support 'urls'; use a single 'value' URL"
        )

    raw_value = item.get("value", "")
    if kind == "url" and isinstance(raw_value, list):
        raise ValueError(
            f"source '{source_name}' does not support URL arrays; use one URL in 'value'"
        )

    if kind == "models_dev_api":
        if raw_value in (None, ""):
            return "default"
        value = str(raw_value).strip()
        if not value:
            raise ValueError(f"source '{source_name}' value must be a non-empty string")
        return value

    value = str(raw_value).strip()
    if not value:
        raise ValueError(f"source '{source_name}' value must be a non-empty string")
    return value
