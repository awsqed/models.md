import json
from pathlib import Path

import pytest
from models_pipeline.config import DEFAULT_MAX_CHARS_PER_SOURCE, load


def _write_config(tmp_path: Path, payload: dict[str, object]) -> Path:
    path = tmp_path / "config.json"
    path.write_text(json.dumps(payload), encoding="utf-8")
    return path


def test_repo_config_models_dev_api_is_summarized() -> None:
    config_path = Path(__file__).resolve().parents[2] / "config.json"
    payload = json.loads(config_path.read_text(encoding="utf-8"))
    source = next(
        item for item in payload["sources"] if item.get("name") == "models_dev_api"
    )
    assert source["summarize"] is True


def test_load_rejects_unsupported_source_type(tmp_path: Path) -> None:
    path = _write_config(
        tmp_path,
        {
            "outputs": ["docs/models/models.catalog.md"],
            "sources": [{"name": "bad", "type": "command", "value": "echo hi"}],
        },
    )

    with pytest.raises(ValueError, match="unsupported type"):
        load(path)


def test_load_accepts_models_dev_api_without_value(tmp_path: Path) -> None:
    path = _write_config(
        tmp_path,
        {
            "outputs": ["docs/models/models.catalog.md"],
            "sources": [{"name": "api", "type": "models_dev_api"}],
        },
    )

    sources, _, runtime = load(path)

    assert sources[0].value == "default"
    assert sources[0].to_toon is False
    assert sources[0].summarize is None
    assert runtime.max_chars_per_source == DEFAULT_MAX_CHARS_PER_SOURCE


def test_load_reads_models_dev_api_to_toon(tmp_path: Path) -> None:
    path = _write_config(
        tmp_path,
        {
            "outputs": ["docs/models/models.catalog.md"],
            "sources": [
                {
                    "name": "api",
                    "type": "models_dev_api",
                    "to_toon": True,
                }
            ],
        },
    )

    sources, _, _ = load(path)

    assert sources[0].to_toon is True


def test_load_rejects_non_boolean_models_dev_api_to_toon(tmp_path: Path) -> None:
    path = _write_config(
        tmp_path,
        {
            "outputs": ["docs/models/models.catalog.md"],
            "sources": [
                {
                    "name": "api",
                    "type": "models_dev_api",
                    "to_toon": "yes",
                }
            ],
        },
    )

    with pytest.raises(ValueError, match="to_toon must be a boolean"):
        load(path)


def test_load_rejects_to_toon_for_non_models_dev_api(tmp_path: Path) -> None:
    path = _write_config(
        tmp_path,
        {
            "outputs": ["docs/models/models.catalog.md"],
            "sources": [
                {
                    "name": "seed",
                    "type": "text",
                    "value": "body",
                    "to_toon": True,
                }
            ],
        },
    )

    with pytest.raises(ValueError, match="only supported for models_dev_api"):
        load(path)


def test_load_reads_source_summarize_flag(tmp_path: Path) -> None:
    path = _write_config(
        tmp_path,
        {
            "outputs": ["docs/models/models.catalog.md"],
            "sources": [
                {"name": "a", "type": "text", "value": "A", "summarize": True},
                {"name": "b", "type": "text", "value": "B", "summarize": False},
                {"name": "c", "type": "text", "value": "C"},
            ],
        },
    )

    sources, _, _ = load(path)

    assert sources[0].summarize is True
    assert sources[1].summarize is False
    assert sources[2].summarize is None


def test_load_rejects_non_boolean_source_summarize(tmp_path: Path) -> None:
    path = _write_config(
        tmp_path,
        {
            "outputs": ["docs/models/models.catalog.md"],
            "sources": [
                {"name": "bad", "type": "text", "value": "seed", "summarize": "yes"}
            ],
        },
    )

    with pytest.raises(ValueError, match="summarize must be a boolean"):
        load(path)
