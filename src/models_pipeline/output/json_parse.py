import json
import re

from models_pipeline.output.json_extract import extract_first_json_object


def parse_json_object(raw: str) -> dict[str, object]:
    candidates: list[str] = []
    seen: set[str] = set()

    def add(candidate: str) -> None:
        val = candidate.strip().lstrip("\ufeff")
        if val and val not in seen:
            seen.add(val)
            candidates.append(val)

    add(raw)
    for match in re.finditer(
        r"```(?:json)?\s*([\s\S]*?)\s*```", raw, flags=re.IGNORECASE
    ):
        add(match.group(1))
    add(extract_first_json_object(raw))

    errors: list[str] = []
    for candidate in candidates:
        try:
            parsed = json.loads(candidate)
        except json.JSONDecodeError as exc:
            errors.append(f"{exc.msg} at line {exc.lineno} col {exc.colno}")
            continue
        if not isinstance(parsed, dict):
            errors.append("top-level JSON value is not an object")
            continue
        return parsed

    preview = raw.strip().replace("\n", "\\n")[:220]
    detail = errors[0] if errors else "no JSON object candidate found"
    raise ValueError(
        f"LLM response is not a valid JSON object ({detail}). Preview: {preview}"
    )
