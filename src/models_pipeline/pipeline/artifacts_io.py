from pathlib import Path

from models_pipeline.pipeline.log_io import write_json, write_text


def write_json_artifact(run_dir: Path, relative_path: str, payload: object) -> str:
    path = run_dir / relative_path
    write_json(path, payload)
    return relative_path


def write_text_artifact(run_dir: Path, relative_path: str, content: str) -> str:
    path = run_dir / relative_path
    write_text(path, content)
    return relative_path
