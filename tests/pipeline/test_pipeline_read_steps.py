from pathlib import Path

from models_pipeline.config import PipelineConfig, SourceItem, SummarizerConfig
from models_pipeline.pipeline import LoadedConfig
from models_pipeline.pipeline.step_read import step_load_schema, step_read_sources


def test_step_load_schema_reads_file(tmp_path: Path) -> None:
    schema_path = tmp_path / "schema.yaml"
    schema_path.write_text("type: object\n", encoding="utf-8")
    assert step_load_schema(schema_path) == "type: object\n"


def test_step_read_sources_uses_summarizer(tmp_path: Path) -> None:
    loaded = LoadedConfig(
        path=Path("unused"),
        model="m",
        api_base_url="https://example.com/v1",
        source_items=[
            SourceItem(name="seed", kind="text", value="original", summarize=True)
        ],
        output_names=["docs/models/a.md"],
        runtime=PipelineConfig(max_chars_per_source=100),
    )

    def summarizer(_name: str, _text: str) -> str:
        return "summary"

    blobs = step_read_sources(loaded, tmp_path, summarizer=summarizer)
    assert blobs == [("seed", "summary", True)]


def test_step_read_sources_without_summarizer(tmp_path: Path) -> None:
    loaded = LoadedConfig(
        path=Path("unused"),
        model="m",
        api_base_url="https://example.com/v1",
        source_items=[SourceItem(name="seed", kind="text", value="body")],
        output_names=["docs/models/a.md"],
        runtime=PipelineConfig(max_chars_per_source=100),
    )

    blobs = step_read_sources(loaded, tmp_path, summarizer=None)
    assert blobs == [("seed", "body", False)]


def test_step_read_sources_uses_global_summarizer_default(tmp_path: Path) -> None:
    loaded = LoadedConfig(
        path=Path("unused"),
        model="m",
        api_base_url="https://example.com/v1",
        source_items=[SourceItem(name="seed", kind="text", value="original")],
        output_names=["docs/models/a.md"],
        runtime=PipelineConfig(
            max_chars_per_source=100,
            summarizer=SummarizerConfig(enabled=True),
        ),
    )

    def summarizer(_name: str, _text: str) -> str:
        return "summary"

    blobs = step_read_sources(loaded, tmp_path, summarizer=summarizer)
    assert blobs == [("seed", "summary", True)]


def test_step_read_sources_source_override_disables_global_summarizer(
    tmp_path: Path,
) -> None:
    loaded = LoadedConfig(
        path=Path("unused"),
        model="m",
        api_base_url="https://example.com/v1",
        source_items=[
            SourceItem(name="seed", kind="text", value="original", summarize=False)
        ],
        output_names=["docs/models/a.md"],
        runtime=PipelineConfig(
            max_chars_per_source=100,
            summarizer=SummarizerConfig(enabled=True),
        ),
    )

    def summarizer(_name: str, _text: str) -> str:
        return "summary"

    blobs = step_read_sources(loaded, tmp_path, summarizer=summarizer)
    assert blobs == [("seed", "original", False)]
