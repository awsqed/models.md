import contextlib
import json
import sys
import time
import traceback
from collections.abc import Generator
from pathlib import Path

from models_pipeline.pipeline.log_io import write_json, write_text
from models_pipeline.pipeline.log_utils import slugify, utc_iso


class RunLogger:
    def __init__(self, run_dir: Path):
        self.run_dir = run_dir
        self.events_path = run_dir / "events.jsonl"
        self.sequence = 0

    def event(self, kind: str, payload: dict[str, object]) -> None:
        record = {"ts": utc_iso(), "kind": kind, "payload": payload}
        line = json.dumps(record, ensure_ascii=False, default=str)
        self.events_path.parent.mkdir(parents=True, exist_ok=True)
        with self.events_path.open("a", encoding="utf-8") as handle:
            handle.write(line + "\n")

    @contextlib.contextmanager
    def step(
        self, name: str, step_input: dict[str, object]
    ) -> Generator[dict[str, object], None, None]:
        self.sequence += 1
        step_id = f"{self.sequence:02d}_{slugify(name)}"
        step_dir = self.run_dir / "steps" / step_id
        step_dir.mkdir(parents=True, exist_ok=False)
        write_json(step_dir / "input.json", step_input)
        self.event(
            "step.start",
            {
                "step": name,
                "step_id": step_id,
                "input_file": str(step_dir / "input.json"),
            },
        )
        output: dict[str, object] = {}
        started_at = time.perf_counter()
        try:
            yield output
        except Exception as exc:
            duration_ms = int((time.perf_counter() - started_at) * 1000)
            elapsed_s = duration_ms / 1000
            trace_path = step_dir / "error.traceback.txt"
            write_text(trace_path, traceback.format_exc())
            write_json(
                step_dir / "error.json",
                {
                    "type": exc.__class__.__name__,
                    "message": str(exc),
                    "duration_ms": duration_ms,
                    "traceback_file": str(trace_path),
                },
            )
            self.event(
                "step.error",
                {
                    "step": name,
                    "step_id": step_id,
                    "duration_ms": duration_ms,
                    "error_type": exc.__class__.__name__,
                    "error_message": str(exc),
                    "traceback_file": str(trace_path),
                },
            )
            print(
                f"[step]  {name} elapsed={elapsed_s:.3f}s ({duration_ms}ms) status=error",
                file=sys.stderr,
            )
            raise

        write_json(step_dir / "output.json", output)
        duration_ms = int((time.perf_counter() - started_at) * 1000)
        elapsed_s = duration_ms / 1000
        self.event(
            "step.success",
            {
                "step": name,
                "step_id": step_id,
                "duration_ms": duration_ms,
                "output_file": str(step_dir / "output.json"),
            },
        )
        print(f"[step]  {name} elapsed={elapsed_s:.3f}s ({duration_ms}ms)")
