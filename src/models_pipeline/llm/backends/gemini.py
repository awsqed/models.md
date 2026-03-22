from typing import Any

from google import genai
from google.genai import errors as genai_errors, types as genai_types

from models_pipeline.llm.errors import LLMFatalError, LLMRetryableError
from models_pipeline.llm.types import ChatRequest, ChatResponse

_RETRYABLE_STATUS_CODES = {408, 429, 500, 502, 503, 504}


class GeminiBackend:
    def complete(self, request: ChatRequest, api_key: str) -> ChatResponse:
        client = genai.Client(api_key=api_key)

        system_parts: list[str] = []
        history: list[Any] = []

        for m in request.messages:
            if m.role == "system":
                system_parts.append(m.content)
            elif m.role == "user":
                history.append(
                    genai_types.Content(
                        role="user", parts=[genai_types.Part(text=m.content)]
                    )
                )
            elif m.role == "assistant":
                history.append(
                    genai_types.Content(
                        role="model", parts=[genai_types.Part(text=m.content)]
                    )
                )

        config_kwargs: dict[str, object] = {}
        if request.max_output_tokens is not None:
            config_kwargs["max_output_tokens"] = request.max_output_tokens
        if system_parts:
            config_kwargs["system_instruction"] = "\n\n".join(system_parts)
        if request.reasoning:
            config_kwargs["thinking_config"] = genai_types.ThinkingConfig(
                thinking_budget=5000
            )

        generate_config = genai_types.GenerateContentConfig(**config_kwargs) if config_kwargs else None  # type: ignore

        try:
            response = client.models.generate_content(
                model=request.model,
                contents=history,
                config=generate_config,
            )
        except genai_errors.APIError as exc:
            status = getattr(exc, "status_code", None) or getattr(exc, "code", None)
            msg = f"LLM API error for model '{request.model}': {exc}"
            if isinstance(status, int) and status in _RETRYABLE_STATUS_CODES:
                raise LLMRetryableError(msg, status_code=status) from exc
            raise LLMFatalError(msg, status_code=status) from exc
        except Exception as exc:
            msg_lower = str(exc).lower()
            if "timeout" in msg_lower or "timed out" in msg_lower:
                raise LLMRetryableError(
                    f"LLM request timed out for model '{request.model}'"
                ) from exc
            raise LLMFatalError(
                f"LLM error for model '{request.model}': {exc}"
            ) from exc

        return _extract_response(response, request.model)


def _extract_response(response: object, model: str) -> ChatResponse:
    # Extract text from the response
    text = getattr(response, "text", None)
    if isinstance(text, str) and text:
        content = text
    else:
        # Try candidates
        candidates = getattr(response, "candidates", None) or []
        parts: list[str] = []
        for candidate in candidates:
            candidate_content = getattr(candidate, "content", None)
            if candidate_content is None:
                continue
            for part in getattr(candidate_content, "parts", []):
                part_text = getattr(part, "text", None)
                if isinstance(part_text, str) and part_text:
                    parts.append(part_text)
        content = "".join(parts)

    if not content:
        finish_reason = None
        candidates = getattr(response, "candidates", None) or []
        if candidates:
            finish_reason = getattr(candidates[0], "finish_reason", None)
        raise LLMFatalError(
            f"LLM API returned empty content from model '{model}' "
            f"(finish_reason={finish_reason!r})"
        )

    # Check for truncation
    candidates = getattr(response, "candidates", None) or []
    if candidates:
        finish_reason = str(getattr(candidates[0], "finish_reason", "") or "").upper()
        if finish_reason in {"MAX_TOKENS", "LENGTH"}:
            raise LLMFatalError(
                f"LLM response truncated (finish_reason={finish_reason!r}). "
                "Increase max_output_tokens or reduce prompt size."
            )

    usage_metadata = getattr(response, "usage_metadata", None)
    input_tokens = _coerce_int(getattr(usage_metadata, "prompt_token_count", 0))
    output_tokens = _coerce_int(getattr(usage_metadata, "candidates_token_count", 0))
    return ChatResponse(
        content=content,
        usage={
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
            "total_tokens": input_tokens + output_tokens,
        },
    )


def _coerce_int(value: object) -> int:
    if isinstance(value, bool):
        return int(value)
    if isinstance(value, int):
        return value
    if isinstance(value, float):
        return int(value)
    if isinstance(value, str) and value.strip().isdigit():
        return int(value.strip())
    return 0
