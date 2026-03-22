"""Parse raw LLM response text into output markdown mappings."""

from models_pipeline.output.json_parse import parse_json_object


def parse(raw: str, allowed_outputs: list[str]) -> dict[str, str]:
    """Extract the JSON object from *raw* and validate output names."""
    data = parse_json_object(raw)
    allowed = set(allowed_outputs)
    result: dict[str, str] = {}
    for key, value in data.items():
        if key not in allowed:
            raise ValueError(f"Unexpected output file in LLM response: {key!r}")
        text = value if isinstance(value, str) else str(value)
        if not text.strip():
            raise ValueError(f"LLM returned empty content for {key!r}")
        result[key] = text if text.endswith("\n") else text + "\n"

    extra = [name for name in result if name not in allowed]
    if extra:
        raise ValueError("Unexpected output files: " + ", ".join(sorted(extra)))
    missing = [name for name in allowed_outputs if name not in result]
    if missing:
        raise ValueError("LLM response is missing output files: " + ", ".join(missing))
    return result
