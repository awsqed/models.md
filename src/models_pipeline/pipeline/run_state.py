from dataclasses import dataclass, field

from models_pipeline.pipeline.types import LoadedConfig, PromptBundle


@dataclass
class RunSessionState:
    loaded: LoadedConfig | None = None
    schema_text: str = ""
    source_blobs: list[tuple[str, str, bool]] = field(default_factory=list)
    bundle: PromptBundle | None = None
    raw: str = ""
    llm_usage: dict[str, int] = field(default_factory=dict)
    outputs: dict[str, str] = field(default_factory=dict)
    summarizer_calls: list[dict[str, object]] = field(default_factory=list)
    exit_code: int = 0
    completed_until: str = ""
