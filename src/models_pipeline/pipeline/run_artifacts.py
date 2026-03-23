from pathlib import Path

from models_pipeline.pipeline.artifacts_io import (
    write_json_artifact,
    write_text_artifact,
)
from models_pipeline.pipeline.artifacts_llm import (
    write_llm_request as write_llm_request_artifact,
    write_llm_response as write_llm_response_artifact,
)
from models_pipeline.pipeline.artifacts_meta import (
    write_run_meta as write_run_meta_artifact,
    write_run_status as write_run_status_artifact,
)
from models_pipeline.pipeline.artifacts_outputs import (
    write_outputs as write_outputs_artifact,
)
from models_pipeline.pipeline.artifacts_sources import (
    write_sources as write_sources_artifact,
    write_summarizer_calls as write_summarizer_calls_artifact,
)


class RunArtifacts:
    def __init__(self, run_dir: Path):
        self.run_dir = run_dir

    def write_run_meta(self, until_step: str) -> None:
        write_run_meta_artifact(self.run_dir, until_step)

    def write_resolved_config(self, payload: dict[str, object]) -> str:
        return write_json_artifact(self.run_dir, "config.resolved.json", payload)

    def write_schema(self, schema_text: str) -> str:
        return write_text_artifact(self.run_dir, "schema.yaml", schema_text)

    def write_sources(
        self,
        source_blobs: list[tuple[str, str, bool]],
        *,
        capture_content: bool,
    ) -> list[dict[str, object]]:
        return write_sources_artifact(
            self.run_dir, source_blobs, capture_content=capture_content
        )

    def write_summarizer_calls(
        self, summarizer_calls: list[dict[str, object]]
    ) -> str | None:
        return write_summarizer_calls_artifact(self.run_dir, summarizer_calls)

    def write_prompt(self, filename: str, content: str) -> str:
        return write_text_artifact(self.run_dir, filename, content)

    def write_llm_request(self, payload: dict[str, object]) -> str:
        return write_llm_request_artifact(self.run_dir, payload)

    def write_llm_response(
        self,
        content: str,
        usage: dict[str, int],
        *,
        capture_text: bool,
    ) -> dict[str, str]:
        return write_llm_response_artifact(
            self.run_dir,
            content,
            usage,
            capture_text=capture_text,
        )

    def write_outputs(
        self, outputs: dict[str, str], *, capture_content: bool
    ) -> list[dict[str, object]]:
        return write_outputs_artifact(
            self.run_dir, outputs, capture_content=capture_content
        )

    def write_run_status(
        self,
        *,
        status: str,
        exit_code: int,
        until_step: str,
        completed_until: str,
        duration_ms: int,
    ) -> str:
        return write_run_status_artifact(
            self.run_dir,
            status=status,
            exit_code=exit_code,
            until_step=until_step,
            completed_until=completed_until,
            duration_ms=duration_ms,
        )
