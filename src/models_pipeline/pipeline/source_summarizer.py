from collections.abc import Callable

from models_pipeline.llm import ChatMessage, ChatRequest, request_chat_completion
from models_pipeline.pipeline.types import LoadedConfig
from models_pipeline.prompt import build_summary_prompt
from models_pipeline.sources import Summarizer


def build_source_summarizer(
    loaded: LoadedConfig, *, record_call: Callable[[dict[str, object]], None]
) -> Summarizer | None:
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
        record_call(
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
