from pathlib import Path

from models_pipeline.config import PipelineConfig, SourceItem
from models_pipeline.llm import ChatResponse
from models_pipeline.pipeline import LoadedConfig, PromptBundle
from models_pipeline.pipeline.step_process import (
    step_build_prompt,
    step_call_llm,
    step_parse_outputs,
    step_write_outputs,
)


def test_step_build_prompt_returns_phase4_bundle() -> None:
    bundle = step_build_prompt(
        blobs=[("seed", "body")],
        schema_text="schema",
        output_names=["docs/models/a.md"],
    )
    assert isinstance(bundle, PromptBundle)
    assert "Return only a single JSON object" in bundle.system
    assert "docs/models/a.md" in bundle.user


def test_step_call_llm_returns_response_with_usage(monkeypatch) -> None:
    loaded = LoadedConfig(
        path=Path("unused"),
        model="demo-model",
        api_base_url="https://example.com/v1",
        source_items=[SourceItem(name="seed", kind="text", value="body")],
        output_names=["docs/models/a.md"],
        runtime=PipelineConfig(),
    )
    bundle = PromptBundle(system="system", user="user")

    def fake_request(_request):
        return ChatResponse(
            content='{"docs/models/a.md":"# ok\\n"}',
            usage={"input_tokens": 3, "output_tokens": 4, "total_tokens": 7},
        )

    monkeypatch.setattr(
        "models_pipeline.pipeline.step_process.llm.request_chat_completion",
        fake_request,
    )

    response = step_call_llm(loaded, bundle)

    assert response.content == '{"docs/models/a.md":"# ok\\n"}'
    assert response.usage == {"input_tokens": 3, "output_tokens": 4, "total_tokens": 7}


def test_step_parse_outputs_validates_expected_names() -> None:
    raw = '{"docs/models/a.md":"# a\\n"}'
    outputs = step_parse_outputs(raw, ["docs/models/a.md"])
    assert outputs == {"docs/models/a.md": "# a\n"}


def test_step_write_outputs_respects_check_mode(tmp_path: Path) -> None:
    outputs = {"docs/models/a.md": "# a\n"}
    assert step_write_outputs(outputs, root=tmp_path, check=False) is True
    assert step_write_outputs(outputs, root=tmp_path, check=True) is True
