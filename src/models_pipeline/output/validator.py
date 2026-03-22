"""Validation helpers for output markdown mappings."""


def validate(outputs: dict[str, str], allowed_outputs: list[str]) -> None:
    allowed = set(allowed_outputs)
    extra = [name for name in outputs if name not in allowed]
    if extra:
        raise ValueError("Unexpected output files: " + ", ".join(sorted(extra)))
    missing = [name for name in allowed_outputs if name not in outputs]
    if missing:
        raise ValueError("LLM response is missing output files: " + ", ".join(missing))
    for name, content in outputs.items():
        if not isinstance(content, str) or not content.strip():
            raise ValueError(f"LLM returned empty content for {name!r}")
