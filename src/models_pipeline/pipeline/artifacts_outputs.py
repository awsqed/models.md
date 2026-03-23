from pathlib import Path

from models_pipeline.pipeline.artifacts_io import (
    write_json_artifact,
    write_text_artifact,
)


def write_outputs(
    run_dir: Path, outputs: dict[str, str], *, capture_content: bool
) -> list[dict[str, object]]:
    output_index = [
        {"name": name, "chars": len(content)} for name, content in outputs.items()
    ]
    write_json_artifact(run_dir, "outputs.index.json", output_index)
    if capture_content:
        for name, content in outputs.items():
            write_text_artifact(run_dir, f"outputs/{name}", content)
    return output_index
