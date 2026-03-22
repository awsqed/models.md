import json
from pathlib import Path

import pytest
from models_pipeline.config import PipelineConfig, SourceItem
from models_pipeline.llm import ChatResponse
from models_pipeline.pipeline import LoadedConfig, PipelineOptions, PromptBundle, run


def test_run_until_step_executes_prerequisites(monkeypatch, tmp_path: Path) -> None:
    call_order: list[str] = []

    config_path = tmp_path / "config.json"
    config_path.write_text(
        json.dumps(
            {
                "outputs": ["docs/models/a.md"],
                "llm": {"api_base_url": "https://example.com/v1"},
                "logging": {
                    "capture_sources": False,
                    "capture_prompts": False,
                    "capture_llm_io": False,
                    "capture_outputs": False,
                },
                "sources": [{"name": "seed", "type": "text", "value": "body"}],
            }
        ),
        encoding="utf-8",
    )

    def fake_load_config(options: PipelineOptions, _root: Path) -> LoadedConfig:
        call_order.append("load_config")
        return LoadedConfig(
            path=options.config_path.resolve(),
            model="m",
            api_base_url="https://example.com/v1",
            source_items=[SourceItem(name="seed", kind="text", value="body")],
            output_names=["docs/models/a.md"],
            runtime=PipelineConfig(),
        )

    def fake_ensure_crawl(_loaded: LoadedConfig) -> None:
        call_order.append("ensure_crawl_support")

    def fake_load_schema(_schema: Path) -> str:
        call_order.append("load_schema")
        return "schema"

    def fake_read_sources(
        _loaded: LoadedConfig,
        _root: Path,
        summarizer=None,
        crawl_debug_root: Path | None = None,
    ) -> list[tuple[str, str, bool]]:
        call_order.append("read_sources")
        assert summarizer is None
        assert crawl_debug_root is None
        return [("seed", "body", False)]

    def fake_build_prompt(
        blobs: list[tuple[str, str]], schema_text: str, output_names: list[str]
    ) -> PromptBundle:
        call_order.append("build_prompt")
        assert blobs == [("seed", "body")]
        assert schema_text == "schema"
        assert output_names == ["docs/models/a.md"]
        return PromptBundle(system="sys", user="usr")

    monkeypatch.setattr(
        "models_pipeline.pipeline.run_session.step_load_config", fake_load_config
    )
    monkeypatch.setattr(
        "models_pipeline.pipeline.run_session.step_ensure_crawl", fake_ensure_crawl
    )
    monkeypatch.setattr(
        "models_pipeline.pipeline.run_session.step_load_schema", fake_load_schema
    )
    monkeypatch.setattr(
        "models_pipeline.pipeline.run_session.step_read_sources", fake_read_sources
    )
    monkeypatch.setattr(
        "models_pipeline.pipeline.run_session.step_build_prompt", fake_build_prompt
    )
    monkeypatch.setattr(
        "models_pipeline.pipeline.run_session.step_call_llm",
        lambda *_args, **_kwargs: pytest.fail("call_llm should not run"),
    )
    monkeypatch.setattr(
        "models_pipeline.pipeline.run_session.step_parse_outputs",
        lambda *_args, **_kwargs: pytest.fail("parse_outputs should not run"),
    )
    monkeypatch.setattr(
        "models_pipeline.pipeline.run_session.step_write_outputs",
        lambda *_args, **_kwargs: pytest.fail("write_outputs should not run"),
    )

    options = PipelineOptions(
        config_path=config_path,
        until_step="build_prompt",
    )
    exit_code = run(options, root=tmp_path)

    assert exit_code == 0
    assert call_order == [
        "load_config",
        "ensure_crawl_support",
        "load_schema",
        "read_sources",
        "build_prompt",
    ]


def test_run_call_llm_writes_structured_response_log(
    monkeypatch, tmp_path: Path
) -> None:
    config_path = tmp_path / "config.json"
    config_path.write_text(
        json.dumps(
            {
                "outputs": ["docs/models/a.md"],
                "llm": {"api_base_url": "https://example.com/v1"},
                "sources": [{"name": "seed", "type": "text", "value": "body"}],
            }
        ),
        encoding="utf-8",
    )

    monkeypatch.setattr(
        "models_pipeline.pipeline.run_session.step_load_schema",
        lambda _schema: "schema",
    )
    monkeypatch.setattr(
        "models_pipeline.pipeline.run_session.step_call_llm",
        lambda *_args, **_kwargs: ChatResponse(
            content='{"docs/models/a.md":"# a\\n"}',
            usage={"input_tokens": 10, "output_tokens": 5, "total_tokens": 15},
        ),
    )

    exit_code = run(
        PipelineOptions(config_path=config_path, until_step="call_llm"), root=tmp_path
    )
    assert exit_code == 0

    run_dirs = sorted((tmp_path / "logs" / "runs").iterdir())
    assert run_dirs
    run_dir = run_dirs[-1]

    response_payload = json.loads((run_dir / "llm.response.json").read_text("utf-8"))
    assert response_payload == {
        "content": '{"docs/models/a.md":"# a\\n"}',
        "usage": {"input_tokens": 10, "output_tokens": 5, "total_tokens": 15},
    }

    call_llm_output = json.loads(
        (run_dir / "steps" / "06_call_llm" / "output.json").read_text("utf-8")
    )
    assert call_llm_output["response_json_file"] == "llm.response.json"
    assert call_llm_output["usage"] == {
        "input_tokens": 10,
        "output_tokens": 5,
        "total_tokens": 15,
    }


def test_run_read_sources_marks_summarized_sources(monkeypatch, tmp_path: Path) -> None:
    config_path = tmp_path / "config.json"
    config_path.write_text(
        json.dumps(
            {
                "outputs": ["docs/models/a.md"],
                "llm": {"api_base_url": "https://example.com/v1"},
                "logging": {
                    "capture_sources": False,
                    "capture_prompts": False,
                    "capture_llm_io": False,
                    "capture_outputs": False,
                },
                "sources": [{"name": "seed", "type": "text", "value": "body"}],
            }
        ),
        encoding="utf-8",
    )

    monkeypatch.setattr(
        "models_pipeline.pipeline.run_session.step_load_schema",
        lambda _schema: "schema",
    )
    monkeypatch.setattr(
        "models_pipeline.pipeline.run_session.step_read_sources",
        lambda *_args, **_kwargs: [("seed", "summary", True)],
    )

    exit_code = run(
        PipelineOptions(config_path=config_path, until_step="read_sources"),
        root=tmp_path,
    )
    assert exit_code == 0

    run_dirs = sorted((tmp_path / "logs" / "runs").iterdir())
    assert run_dirs
    run_dir = run_dirs[-1]

    sources_index = json.loads((run_dir / "sources.index.json").read_text("utf-8"))
    assert sources_index == [
        {
            "name": "seed",
            "chars": len("summary"),
            "file": None,
            "summarized": True,
        }
    ]

    read_sources_output = json.loads(
        (run_dir / "steps" / "04_read_sources" / "output.json").read_text("utf-8")
    )
    assert read_sources_output["sources"][0]["summarized"] is True


def test_run_prints_step_elapsed_time(monkeypatch, tmp_path: Path, capsys) -> None:
    config_path = tmp_path / "config.json"
    config_path.write_text(
        json.dumps(
            {
                "outputs": ["docs/models/a.md"],
                "llm": {"api_base_url": "https://example.com/v1"},
                "sources": [{"name": "seed", "type": "text", "value": "body"}],
            }
        ),
        encoding="utf-8",
    )

    monkeypatch.setattr(
        "models_pipeline.pipeline.run_session.step_load_schema",
        lambda _schema: "schema",
    )
    monkeypatch.setattr(
        "models_pipeline.pipeline.run_session.step_read_sources",
        lambda *_args, **_kwargs: [("seed", "body", False)],
    )
    monkeypatch.setattr(
        "models_pipeline.pipeline.run_session.step_build_prompt",
        lambda *_args, **_kwargs: PromptBundle(system="sys", user="usr"),
    )

    exit_code = run(
        PipelineOptions(config_path=config_path, until_step="build_prompt"),
        root=tmp_path,
    )

    assert exit_code == 0
    captured = capsys.readouterr()
    assert "[step]  load_config elapsed=" in captured.out
    assert "[step]  ensure_crawl_support elapsed=" in captured.out
    assert "[step]  load_schema elapsed=" in captured.out
    assert "[step]  read_sources elapsed=" in captured.out
    assert "[step]  build_prompt elapsed=" in captured.out
