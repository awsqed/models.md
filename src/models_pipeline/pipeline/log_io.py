import json
from pathlib import Path


def _json_default(value: object) -> str:
    if isinstance(value, Path):
        return str(value)
    return str(value)


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def write_json(path: Path, payload: object) -> None:
    write_text(
        path,
        json.dumps(payload, ensure_ascii=False, indent=2, default=_json_default) + "\n",
    )
