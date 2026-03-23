from models_pipeline.llm import ChatMessage, ChatRequest
from models_pipeline.pipeline.step_config import source_config_dict
from models_pipeline.pipeline.types import LoadedConfig, PromptBundle


def resolved_config_payload(loaded: LoadedConfig, *, check: bool) -> dict[str, object]:
    return {
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
        "check": check,
        "outputs": loaded.output_names,
        "source_count": len(loaded.source_items),
        "sources": [source_config_dict(item) for item in loaded.source_items],
    }


def llm_request_payload(
    loaded: LoadedConfig, bundle: PromptBundle
) -> tuple[ChatRequest, dict[str, object]]:
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
        "messages": [{"role": m.role, "content": m.content} for m in request.messages],
    }
    return request, payload


def run_status(
    *,
    until_step: str,
    exit_code: int,
) -> str:
    partial_run = bool(until_step) and until_step != "write_outputs"
    status = (
        "partial_success"
        if partial_run
        else ("success" if exit_code == 0 else "check_failed")
    )
    if exit_code != 0:
        status = "check_failed"
    return status
