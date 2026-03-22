import json
from pathlib import Path

from models_pipeline.config import PipelineConfig, SourceItem
from models_pipeline.pipeline import LoadedConfig, PIPELINE_STEP_ORDER, PipelineOptions
from models_pipeline.pipeline.step_config import step_ensure_crawl, step_load_config


def test_step_load_config_reads_and_overrides(tmp_path: Path) -> None:
    config_path = tmp_path / "config.json"
    config_path.write_text(
        json.dumps(
            {
                "outputs": ["docs/models/custom.md"],
                "llm": {
                    "model": "configured-model",
                    "api_base_url": "https://api.example.com",
                },
                "sources": [{"name": "seed", "type": "text", "value": "seed"}],
            }
        ),
        encoding="utf-8",
    )
    options = PipelineOptions(
        config_path=config_path,
        model_override="override-model",
        api_base_url_override="https://override.example.com/v1",
    )

    loaded = step_load_config(options, tmp_path)

    assert loaded.path == config_path.resolve()
    assert loaded.model == "override-model"
    assert loaded.api_base_url == "https://override.example.com/v1"
    assert loaded.output_names == ["docs/models/custom.md"]
    assert loaded.source_items[0].name == "seed"


def test_step_ensure_crawl_only_for_url_sources(monkeypatch) -> None:
    called = {"count": 0}

    def fake_ensure_available() -> None:
        called["count"] += 1

    monkeypatch.setattr(
        "models_pipeline.pipeline.step_config.crawl.ensure_available",
        fake_ensure_available,
    )
    loaded_without_url = LoadedConfig(
        path=Path("unused"),
        model="m",
        api_base_url="https://example.com/v1",
        source_items=[SourceItem(name="seed", kind="text", value="x")],
        output_names=["docs/models/a.md"],
        runtime=PipelineConfig(),
    )
    loaded_with_url = LoadedConfig(
        path=Path("unused"),
        model="m",
        api_base_url="https://example.com/v1",
        source_items=[SourceItem(name="u", kind="url", value="https://example.com")],
        output_names=["docs/models/a.md"],
        runtime=PipelineConfig(),
    )

    step_ensure_crawl(loaded_without_url)
    step_ensure_crawl(loaded_with_url)

    assert called["count"] == 1


def test_pipeline_step_order_matches_expected_cli_choices() -> None:
    assert PIPELINE_STEP_ORDER == (
        "load_config",
        "ensure_crawl_support",
        "load_schema",
        "read_sources",
        "build_prompt",
        "call_llm",
        "parse_outputs",
        "write_outputs",
    )
