from dataclasses import dataclass
from pathlib import Path

from models_pipeline.config import PipelineConfig, SourceItem

PIPELINE_STEP_ORDER = (
    "load_config",
    "ensure_crawl_support",
    "load_schema",
    "read_sources",
    "build_prompt",
    "call_llm",
    "parse_outputs",
    "write_outputs",
)


@dataclass(frozen=True)
class PipelineOptions:
    config_path: Path
    model_override: str = ""
    api_base_url_override: str = ""
    check: bool = False
    until_step: str = ""


@dataclass(frozen=True)
class LoadedConfig:
    path: Path
    model: str
    api_base_url: str
    source_items: list[SourceItem]
    output_names: list[str]
    runtime: PipelineConfig


@dataclass(frozen=True)
class PromptBundle:
    system: str
    user: str
