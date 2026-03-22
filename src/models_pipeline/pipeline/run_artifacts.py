import platform
import sys
from pathlib import Path

from models_pipeline.pipeline.log_io import write_json, write_text
from models_pipeline.pipeline.log_utils import utc_iso


class RunArtifacts:
    def __init__(self, run_dir: Path):
        self.run_dir = run_dir

    def write_run_meta(self, until_step: str) -> None:
        write_json(
            self.run_dir / "run.meta.json",
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

    def write_resolved_config(self, payload: dict[str, object]) -> str:
        return self._write_json_artifact("config.resolved.json", payload)

    def write_schema(self, schema_text: str) -> str:
        return self._write_text_artifact("schema.yaml", schema_text)

    def write_sources(
        self,
        source_blobs: list[tuple[str, str, bool]],
        *,
        capture_content: bool,
    ) -> list[dict[str, object]]:
        source_index: list[dict[str, object]] = []
        for index, (name, blob, summarized) in enumerate(source_blobs, start=1):
            filename = f"{index:02d}_{name}.txt"
            source_file: str | None = None
            if capture_content:
                self._write_text_artifact(f"sources/{filename}", blob)
                source_file = filename
            source_index.append(
                {
                    "name": name,
                    "chars": len(blob),
                    "file": source_file,
                    "summarized": summarized,
                }
            )
        self._write_json_artifact("sources.index.json", source_index)
        return source_index

    def write_summarizer_calls(
        self, summarizer_calls: list[dict[str, object]]
    ) -> str | None:
        if not summarizer_calls:
            return None
        return self._write_json_artifact("summarizer.calls.json", summarizer_calls)

    def write_prompt(self, filename: str, content: str) -> str:
        return self._write_text_artifact(filename, content)

    def write_llm_request(self, payload: dict[str, object]) -> str:
        return self._write_json_artifact("llm.request.json", payload)

    def write_llm_response(
        self,
        content: str,
        usage: dict[str, int],
        *,
        capture_text: bool,
    ) -> dict[str, str]:
        files = {
            "response_json_file": self._write_json_artifact(
                "llm.response.json",
                {"content": content, "usage": usage},
            )
        }
        if capture_text:
            files["response_file"] = self._write_text_artifact(
                "llm.response.txt", content
            )
        return files

    def write_outputs(
        self, outputs: dict[str, str], *, capture_content: bool
    ) -> list[dict[str, object]]:
        output_index = [
            {"name": name, "chars": len(content)} for name, content in outputs.items()
        ]
        self._write_json_artifact("outputs.index.json", output_index)
        if capture_content:
            for name, content in outputs.items():
                self._write_text_artifact(f"outputs/{name}", content)
        return output_index

    def write_run_status(
        self,
        *,
        status: str,
        exit_code: int,
        until_step: str,
        completed_until: str,
        duration_ms: int,
    ) -> str:
        return self._write_json_artifact(
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

    def _write_json_artifact(self, relative_path: str, payload: object) -> str:
        path = self.run_dir / relative_path
        write_json(path, payload)
        return relative_path

    def _write_text_artifact(self, relative_path: str, content: str) -> str:
        path = self.run_dir / relative_path
        write_text(path, content)
        return relative_path
