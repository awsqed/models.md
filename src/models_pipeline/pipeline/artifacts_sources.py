from pathlib import Path

from models_pipeline.pipeline.artifacts_io import (
    write_json_artifact,
    write_text_artifact,
)


def write_sources(
    run_dir: Path,
    source_blobs: list[tuple[str, str, bool]],
    *,
    capture_content: bool,
) -> list[dict[str, object]]:
    source_index: list[dict[str, object]] = []
    for index, (name, blob, summarized) in enumerate(source_blobs, start=1):
        filename = f"{index:02d}_{name}.txt"
        source_file: str | None = None
        if capture_content:
            write_text_artifact(run_dir, f"sources/{filename}", blob)
            source_file = filename
        source_index.append(
            {
                "name": name,
                "chars": len(blob),
                "file": source_file,
                "summarized": summarized,
            }
        )
    write_json_artifact(run_dir, "sources.index.json", source_index)
    return source_index


def write_summarizer_calls(
    run_dir: Path, summarizer_calls: list[dict[str, object]]
) -> str | None:
    if not summarizer_calls:
        return None
    return write_json_artifact(run_dir, "summarizer.calls.json", summarizer_calls)
