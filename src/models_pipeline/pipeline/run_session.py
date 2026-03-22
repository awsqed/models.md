import time
from pathlib import Path

from models_pipeline.llm import ChatMessage, ChatRequest, request_chat_completion
from models_pipeline.pipeline.log_runner import RunLogger
from models_pipeline.pipeline.log_utils import create_run_dir
from models_pipeline.pipeline.run_artifacts import RunArtifacts
from models_pipeline.pipeline.run_state import RunSessionState
from models_pipeline.pipeline.step_config import (
    source_config_dict,
    step_ensure_crawl,
    step_load_config,
)
from models_pipeline.pipeline.step_process import (
    step_build_prompt,
    step_call_llm,
    step_parse_outputs,
    step_write_outputs,
)
from models_pipeline.pipeline.step_read import step_load_schema, step_read_sources
from models_pipeline.pipeline.types import (
    LoadedConfig,
    PIPELINE_STEP_ORDER,
    PipelineOptions,
)
from models_pipeline.prompt import build_summary_prompt
from models_pipeline.sources import Summarizer
from models_pipeline.sources.registry import get_source_registry

SCHEMA_FILE = Path(__file__).resolve().parents[3] / "models.schema.yaml"
_STEP_POSITION = {name: index for index, name in enumerate(PIPELINE_STEP_ORDER)}


class PipelineRunSession:
    def __init__(self, options: PipelineOptions, root: Path):
        self.options = options
        self.root = root
        self.until_step = options.until_step.strip()
        if self.until_step and self.until_step not in _STEP_POSITION:
            raise ValueError(
                f"unsupported until_step={self.until_step!r}. Expected one of: {PIPELINE_STEP_ORDER}"
            )

        self.run_started_at = time.perf_counter()
        self.run_dir = create_run_dir((root / "logs/runs").resolve())
        self.logger = RunLogger(self.run_dir)
        self.artifacts = RunArtifacts(self.run_dir)
        self.state = RunSessionState()

    def should_run(self, step_name: str) -> bool:
        if not self.until_step:
            return True
        return _STEP_POSITION[step_name] <= _STEP_POSITION[self.until_step]

    def start(self) -> None:
        print(f"[log]    run_dir={self.run_dir}")
        if self.until_step:
            print(f"[run]    until_step={self.until_step}")
        self.artifacts.write_run_meta(self.until_step)
        self.logger.event(
            "run.start",
            {"run_dir": str(self.run_dir), "until_step": self.until_step or None},
        )

    def _require_loaded(self) -> LoadedConfig:
        if self.state.loaded is None:
            raise RuntimeError("load_config step was not executed")
        return self.state.loaded

    def run_load_config(self) -> None:
        with self.logger.step(
            "load_config",
            {
                "sources_arg": str(self.options.config_path),
                "model_override": self.options.model_override,
                "api_base_url_override": self.options.api_base_url_override,
                "check": self.options.check,
                "until_step": self.until_step or None,
            },
        ) as step_output:
            self.state.loaded = step_load_config(self.options, self.root)
            loaded = self._require_loaded()
            self.artifacts.write_resolved_config(
                {
                    "sources_path": str(loaded.path),
                    "runtime": {
                        "max_chars_per_source": loaded.runtime.max_chars_per_source,
                        "llm": {
                            "model": loaded.model,
                            "api_base_url": loaded.api_base_url,
                            "timeout_seconds": loaded.runtime.llm.timeout_seconds,
                            "max_retries": loaded.runtime.llm.max_retries,
                            "max_output_tokens": loaded.runtime.llm.max_output_tokens,
                            "disable_thinking": loaded.runtime.llm.disable_thinking,
                        },
                        "summarizer": {
                            "enabled": loaded.runtime.summarizer.enabled,
                            "model": loaded.runtime.summarizer.model,
                            "api_base_url": loaded.runtime.summarizer.api_base_url,
                            "timeout_seconds": loaded.runtime.summarizer.timeout_seconds,
                            "max_retries": loaded.runtime.summarizer.max_retries,
                            "max_output_tokens": loaded.runtime.summarizer.max_output_tokens,
                            "disable_thinking": loaded.runtime.summarizer.disable_thinking,
                        },
                        "logging": {
                            "capture_sources": loaded.runtime.logging.capture_sources,
                            "capture_prompts": loaded.runtime.logging.capture_prompts,
                            "capture_llm_io": loaded.runtime.logging.capture_llm_io,
                            "capture_outputs": loaded.runtime.logging.capture_outputs,
                        },
                    },
                    "check": self.options.check,
                    "outputs": loaded.output_names,
                    "source_count": len(loaded.source_items),
                    "sources": [
                        source_config_dict(item) for item in loaded.source_items
                    ],
                }
            )
            step_output.update(
                {
                    "config_path": str(loaded.path),
                    "model": loaded.model,
                    "endpoint": loaded.api_base_url,
                    "source_count": len(loaded.source_items),
                    "outputs": loaded.output_names,
                    "resolved_config_file": "config.resolved.json",
                }
            )
        self.state.completed_until = "load_config"

    def run_ensure_crawl_support(self) -> None:
        loaded = self._require_loaded()
        crawl_kinds = get_source_registry().kinds_requiring_crawl()
        crawl_source_names = [
            item.name for item in loaded.source_items if item.kind in crawl_kinds
        ]
        with self.logger.step(
            "ensure_crawl_support",
            {
                "crawl_source_names": crawl_source_names,
                "crawl_source_count": len(crawl_source_names),
            },
        ) as step_output:
            step_ensure_crawl(loaded)
            step_output.update(
                {"crawl_check_performed": bool(crawl_source_names), "status": "ok"}
            )
        self.state.completed_until = "ensure_crawl_support"

    def run_load_schema(self) -> None:
        with self.logger.step(
            "load_schema", {"schema_path": str(SCHEMA_FILE)}
        ) as step_output:
            self.state.schema_text = step_load_schema(SCHEMA_FILE)
            self.artifacts.write_schema(self.state.schema_text)
            step_output.update(
                {
                    "schema_chars": len(self.state.schema_text),
                    "schema_file": "schema.yaml",
                }
            )
        self.state.completed_until = "load_schema"

    def build_source_summarizer(self) -> Summarizer | None:
        loaded = self._require_loaded()
        if not loaded.runtime.summarizer.enabled:
            return None

        cfg = loaded.runtime.summarizer
        api_base_url = cfg.api_base_url or loaded.api_base_url
        model = cfg.model or loaded.model

        def summarize_source(source_name: str, text: str) -> str:
            summary_system, summary_user = build_summary_prompt(source_name, text)
            response = request_chat_completion(
                ChatRequest(
                    model=model,
                    api_base_url=api_base_url,
                    messages=[
                        ChatMessage(role="system", content=summary_system),
                        ChatMessage(role="user", content=summary_user),
                    ],
                    timeout_seconds=cfg.timeout_seconds,
                    max_retries=cfg.max_retries,
                    max_output_tokens=cfg.max_output_tokens,
                    reasoning=not cfg.disable_thinking,
                )
            )
            summary = response.content.strip() or text
            self.state.summarizer_calls.append(
                {
                    "source_name": source_name,
                    "input_chars": len(text),
                    "summary_chars": len(summary),
                    "returned_empty_content": not response.content.strip(),
                    "usage": response.usage,
                }
            )
            return summary

        return summarize_source

    def run_read_sources(self, source_summarizer: Summarizer | None) -> None:
        loaded = self._require_loaded()
        with self.logger.step(
            "read_sources",
            {
                "root": str(self.root),
                "max_chars_per_source": loaded.runtime.max_chars_per_source,
                "sources": [source_config_dict(item) for item in loaded.source_items],
            },
        ) as step_output:
            self.state.source_blobs = step_read_sources(
                loaded,
                self.root,
                summarizer=source_summarizer,
                crawl_debug_root=(
                    self.run_dir / "steps/04_read_sources/crawl_debug"
                    if loaded.runtime.logging.capture_sources
                    else None
                ),
            )
            source_index = self.artifacts.write_sources(
                self.state.source_blobs,
                capture_content=loaded.runtime.logging.capture_sources,
            )
            step_output.update(
                {
                    "source_count": len(self.state.source_blobs),
                    "sources_index_file": "sources.index.json",
                    "total_source_chars": sum(
                        len(blob) for _, blob, _ in self.state.source_blobs
                    ),
                    "sources": source_index,
                }
            )
            if self.state.summarizer_calls:
                self.artifacts.write_summarizer_calls(self.state.summarizer_calls)
                step_output["summarizer_calls_file"] = "summarizer.calls.json"
                step_output["summarizer_calls"] = self.state.summarizer_calls
            if loaded.runtime.logging.capture_sources:
                step_output["sources"] = [
                    {
                        "name": name,
                        "chars": len(blob),
                        "content": blob,
                        "summarized": summarized,
                    }
                    for name, blob, summarized in self.state.source_blobs
                ]
        self.state.completed_until = "read_sources"

    def run_build_prompt(self) -> None:
        loaded = self._require_loaded()
        with self.logger.step(
            "build_prompt",
            {
                "source_count": len(self.state.source_blobs),
                "schema_chars": len(self.state.schema_text),
            },
        ) as step_output:
            self.state.bundle = step_build_prompt(
                [(name, blob) for name, blob, _ in self.state.source_blobs],
                self.state.schema_text,
                loaded.output_names,
            )
            bundle = self.state.bundle
            if bundle is None:
                raise RuntimeError("build_prompt step failed")
            step_output.update(
                {
                    "system_chars": len(bundle.system),
                    "user_chars": len(bundle.user),
                    "total_chars": len(bundle.system) + len(bundle.user),
                    "system_preview": bundle.system[:500],
                    "user_preview": bundle.user[:500],
                }
            )
            if loaded.runtime.logging.capture_prompts:
                step_output["system_prompt_file"] = self.artifacts.write_prompt(
                    "prompt.system.txt", bundle.system
                )
                step_output["user_prompt_file"] = self.artifacts.write_prompt(
                    "prompt.user.txt", bundle.user
                )
            request = ChatRequest(
                model=loaded.model,
                api_base_url=loaded.api_base_url,
                messages=[
                    ChatMessage(role="system", content=bundle.system),
                    ChatMessage(role="user", content=bundle.user),
                ],
                max_output_tokens=loaded.runtime.llm.max_output_tokens,
                reasoning=not loaded.runtime.llm.disable_thinking,
            )
            payload = {
                "endpoint": loaded.api_base_url,
                "model": loaded.model,
                "messages": [
                    {"role": m.role, "content": m.content} for m in request.messages
                ],
            }
            step_output["llm_request_file"] = self.artifacts.write_llm_request(payload)
            if loaded.runtime.logging.capture_llm_io:
                step_output["llm_request"] = payload
        self.state.completed_until = "build_prompt"

    def run_call_llm(self) -> None:
        loaded = self._require_loaded()
        if self.state.bundle is None:
            raise RuntimeError("build_prompt step must run before call_llm")
        with self.logger.step(
            "call_llm",
            {
                "model": loaded.model,
                "endpoint": loaded.api_base_url,
                "timeout_seconds": loaded.runtime.llm.timeout_seconds,
                "max_retries": loaded.runtime.llm.max_retries,
                "max_output_tokens": loaded.runtime.llm.max_output_tokens,
                "disable_thinking": loaded.runtime.llm.disable_thinking,
                "system_chars": len(self.state.bundle.system),
                "user_chars": len(self.state.bundle.user),
                "request_file": "llm.request.json",
            },
        ) as step_output:
            response = step_call_llm(loaded, self.state.bundle)
            self.state.raw = response.content
            self.state.llm_usage = response.usage
            response_files = self.artifacts.write_llm_response(
                self.state.raw,
                self.state.llm_usage,
                capture_text=loaded.runtime.logging.capture_llm_io,
            )
            step_output["response_json_file"] = response_files["response_json_file"]
            step_output["response_chars"] = len(self.state.raw)
            step_output["usage"] = self.state.llm_usage
            step_output["response_preview"] = self.state.raw[:500]
            if loaded.runtime.logging.capture_llm_io:
                step_output["response_file"] = response_files["response_file"]
                step_output["response"] = self.state.raw
        self.state.completed_until = "call_llm"

    def run_parse_outputs(self) -> None:
        loaded = self._require_loaded()
        with self.logger.step(
            "parse_outputs",
            {
                "response_chars": len(self.state.raw),
                "llm_usage": self.state.llm_usage,
                "response_json_file": "llm.response.json",
                "response_file": (
                    "llm.response.txt"
                    if loaded.runtime.logging.capture_llm_io
                    else None
                ),
            },
        ) as step_output:
            self.state.outputs = step_parse_outputs(self.state.raw, loaded.output_names)
            output_index = self.artifacts.write_outputs(
                self.state.outputs,
                capture_content=loaded.runtime.logging.capture_outputs,
            )
            step_output.update(
                {
                    "output_count": len(self.state.outputs),
                    "outputs_index_file": "outputs.index.json",
                    "outputs_index": output_index,
                    "outputs_root": (
                        "outputs/" if loaded.runtime.logging.capture_outputs else None
                    ),
                    "llm_usage": self.state.llm_usage,
                }
            )
            if loaded.runtime.logging.capture_outputs:
                step_output["outputs"] = self.state.outputs
        self.state.completed_until = "parse_outputs"

    def run_write_outputs(self) -> None:
        with self.logger.step(
            "write_outputs",
            {"check_mode": self.options.check, "output_count": len(self.state.outputs)},
        ) as step_output:
            ok = step_write_outputs(
                self.state.outputs, root=self.root, check=self.options.check
            )
            self.state.exit_code = 0 if ok else 1
            step_output.update(
                {
                    "ok": ok,
                    "mode": "check" if self.options.check else "write",
                    "exit_code": self.state.exit_code,
                }
            )
        self.state.completed_until = "write_outputs"

    def finish(self) -> int:
        duration_ms = int((time.perf_counter() - self.run_started_at) * 1000)
        partial_run = bool(self.until_step) and self.until_step != "write_outputs"
        status = (
            "partial_success"
            if partial_run
            else ("success" if self.state.exit_code == 0 else "check_failed")
        )
        if self.state.exit_code != 0:
            status = "check_failed"

        self.artifacts.write_run_status(
            status=status,
            exit_code=self.state.exit_code,
            until_step=self.until_step,
            completed_until=self.state.completed_until,
            duration_ms=duration_ms,
        )
        self.logger.event(
            "run.end",
            {
                "status": status,
                "exit_code": self.state.exit_code,
                "until_step": self.until_step or None,
                "completed_until": self.state.completed_until or None,
                "duration_ms": duration_ms,
            },
        )
        return self.state.exit_code

    def execute(self) -> int:
        self.start()
        if self.should_run("load_config"):
            self.run_load_config()
        self._require_loaded()

        if self.should_run("ensure_crawl_support"):
            self.run_ensure_crawl_support()
        if self.should_run("load_schema"):
            self.run_load_schema()

        source_summarizer = self.build_source_summarizer()
        if self.should_run("read_sources"):
            self.run_read_sources(source_summarizer)
        if self.should_run("build_prompt"):
            self.run_build_prompt()
        if self.should_run("call_llm"):
            self.run_call_llm()
        if self.should_run("parse_outputs"):
            self.run_parse_outputs()
        if self.should_run("write_outputs"):
            self.run_write_outputs()
        return self.finish()


def run(options: PipelineOptions, root: Path) -> int:
    return PipelineRunSession(options, root).execute()
