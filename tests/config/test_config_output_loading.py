import json
from pathlib import Path

import pytest
from models_pipeline.config import load


def _write_config(tmp_path: Path, payload: dict[str, object]) -> Path:
    path = tmp_path / "config.json"
    path.write_text(json.dumps(payload), encoding="utf-8")
    return path


def test_load_accepts_docs_prefixed_outputs_without_allowlist(tmp_path: Path) -> None:
    path = _write_config(
        tmp_path,
        {
            "outputs": ["docs/models/custom-a.md", "docs/models/custom-b.md"],
            "sources": [{"name": "seed", "type": "text", "value": "ok"}],
        },
    )

    _, outputs, _ = load(path)

    assert outputs == ["docs/models/custom-a.md", "docs/models/custom-b.md"]


@pytest.mark.parametrize(
    "outputs",
    [
        ["models.md"],
        ["/tmp/out.md"],
        ["docs/models/not-markdown.txt"],
    ],
)
def test_load_rejects_invalid_output_paths(
    tmp_path: Path,
    outputs: list[str],
) -> None:
    path = _write_config(
        tmp_path,
        {
            "outputs": outputs,
            "sources": [{"name": "seed", "type": "text", "value": "ok"}],
        },
    )

    with pytest.raises(ValueError, match="output paths must start with 'docs/models/'"):
        load(path)


def test_load_rejects_duplicate_output_paths(tmp_path: Path) -> None:
    path = _write_config(
        tmp_path,
        {
            "outputs": ["docs/models/a.md", "docs/models/a.md"],
            "sources": [{"name": "seed", "type": "text", "value": "ok"}],
        },
    )

    with pytest.raises(ValueError, match="outputs must be unique"):
        load(path)
