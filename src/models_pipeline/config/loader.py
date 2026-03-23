import json
from pathlib import Path

from models_pipeline.config.runtime_builders import build_runtime_config
from models_pipeline.config.schema import DEFAULT_OUTPUTS, PipelineConfig, SourceItem
from models_pipeline.config.source_builders import build_source_item, coerce_source_item
from models_pipeline.config.validators import validate_output_name
from models_pipeline.sources.registry import get_source_registry


def load(path: Path) -> tuple[list[SourceItem], list[str], PipelineConfig]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError("config file must contain a JSON object")

    raw_sources = payload.get("sources", [])
    if not isinstance(raw_sources, list):
        raise ValueError("sources must be an array")

    runtime_config = build_runtime_config(payload)
    supported_kinds = get_source_registry().supported_kinds()

    source_items = [
        build_source_item(coerce_source_item(item), supported_kinds)
        for item in raw_sources
    ]

    outputs = payload.get("outputs", DEFAULT_OUTPUTS)
    if not isinstance(outputs, list):
        raise ValueError("outputs must be an array")
    output_names = [str(n).strip() for n in outputs]
    if not output_names:
        raise ValueError("outputs must define at least one path")
    if len(output_names) != len(set(output_names)):
        raise ValueError("outputs must be unique")
    for output_name in output_names:
        validate_output_name(output_name)

    return source_items, output_names, runtime_config
