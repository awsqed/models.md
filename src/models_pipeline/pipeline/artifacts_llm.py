from pathlib import Path

from models_pipeline.pipeline.artifacts_io import (
    write_json_artifact,
    write_text_artifact,
)


def write_llm_request(run_dir: Path, payload: dict[str, object]) -> str:
    return write_json_artifact(run_dir, "llm.request.json", payload)


def write_llm_response(
    run_dir: Path,
    content: str,
    usage: dict[str, int],
    *,
    capture_text: bool,
) -> dict[str, str]:
    files = {
        "response_json_file": write_json_artifact(
            run_dir,
            "llm.response.json",
            {"content": content, "usage": usage},
        )
    }
    if capture_text:
        files["response_file"] = write_text_artifact(
            run_dir, "llm.response.txt", content
        )
    return files
