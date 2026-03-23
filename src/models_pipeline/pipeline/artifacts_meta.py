import platform
import sys
from pathlib import Path

from models_pipeline.pipeline.artifacts_io import write_json_artifact
from models_pipeline.pipeline.log_utils import utc_iso


def write_run_meta(run_dir: Path, until_step: str) -> None:
    write_json_artifact(
        run_dir,
        "run.meta.json",
        {
            "started_at": utc_iso(),
            "cwd": str(Path.cwd()),
            "argv": sys.argv,
            "python": {
                "version": platform.python_version(),
                "executable": sys.executable,
                "platform": platform.platform(),
            },
            "until_step": until_step or None,
        },
    )


def write_run_status(
    run_dir: Path,
    *,
    status: str,
    exit_code: int,
    until_step: str,
    completed_until: str,
    duration_ms: int,
) -> str:
    return write_json_artifact(
        run_dir,
        "run.status.json",
        {
            "status": status,
            "exit_code": exit_code,
            "until_step": until_step or None,
            "completed_until": completed_until or None,
            "duration_ms": duration_ms,
            "ended_at": utc_iso(),
        },
    )
