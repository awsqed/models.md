import anthropic
from anthropic import APIConnectionError, APIStatusError, APITimeoutError

from models_pipeline.llm.errors import LLMFatalError, LLMRetryableError
from models_pipeline.llm.types import ChatRequest, ChatResponse

_RETRYABLE_STATUS_CODES = {408, 429, 500, 502, 503, 504}


class AnthropicBackend:
    def complete(self, request: ChatRequest, api_key: str) -> ChatResponse:
        base_url = request.api_base_url.strip().rstrip("/")
        client = anthropic.Anthropic(
            api_key=api_key,
            base_url=base_url,
            timeout=float(request.timeout_seconds),
            max_retries=0,
        )

        system_parts: list[str] = []
        messages: list[dict[str, str]] = []
        for m in request.messages:
            if m.role == "system":
                system_parts.append(m.content)
            else:
                messages.append({"role": m.role, "content": m.content})

        create_kwargs: dict[str, object] = {
            "model": request.model,
            "messages": messages,
            "max_tokens": request.max_output_tokens or 4096,
        }
        if system_parts:
            create_kwargs["system"] = "\n\n".join(system_parts)
        if request.reasoning:
            create_kwargs["thinking"] = {"type": "enabled", "budget_tokens": 5000}

        try:
            response = client.messages.create(**create_kwargs)  # type: ignore
        except APIStatusError as exc:
            status = exc.status_code
            detail = str(exc.body) if exc.body is not None else str(exc)
            msg = (
                f"LLM API error {status} for model '{request.model}' "
                f"at {base_url}: {detail}"
            )
            if status in _RETRYABLE_STATUS_CODES:
                raise LLMRetryableError(msg, status_code=status) from exc
            raise LLMFatalError(msg, status_code=status) from exc
        except APITimeoutError as exc:
            raise LLMRetryableError(
                f"LLM request timed out for model '{request.model}' at {base_url} "
                f"after {request.timeout_seconds}s"
            ) from exc
        except APIConnectionError as exc:
            raise LLMRetryableError(
                f"LLM network error for model '{request.model}' at {base_url}: {exc}"
            ) from exc

        payload = response.model_dump(mode="json")
        return _extract_response(payload, request.model, base_url)


def _extract_response(
    payload: dict[str, object], model: str, endpoint: str
) -> ChatResponse:
    content_list = payload.get("content")
    if not isinstance(content_list, list) or not content_list:
        raise LLMFatalError(
            f"LLM API returned empty content from model '{model}' at {endpoint}"
        )

    text_parts: list[str] = []
    for item in content_list:
        if not isinstance(item, dict):
            continue
        item_type = str(item.get("type", "")).strip().lower()
        if item_type == "text":
            text = item.get("text")
            if isinstance(text, str) and text:
                text_parts.append(text)
        elif item_type == "thinking":
            # Include thinking block content only if no text blocks exist (fallback)
            pass

    if not text_parts:
        # Fallback: try thinking blocks
        for item in content_list:
            if not isinstance(item, dict):
                continue
            for key in ("text", "thinking", "content"):
                val = item.get(key)
                if isinstance(val, str) and val:
                    text_parts.append(val)
                    break

    content = "".join(text_parts)

    stop_reason = str(payload.get("stop_reason", "")).strip().lower()
    if stop_reason in {"max_tokens", "length"}:
        raise LLMFatalError(
            f"LLM response truncated (stop_reason={stop_reason!r}, "
            f"content_chars={len(content)}). Increase max_output_tokens or reduce prompt size."
        )
    if not content:
        raise LLMFatalError(
            f"LLM API returned empty content (stop_reason={payload.get('stop_reason')!r})"
        )

    usage_raw = payload.get("usage") or {}
    if not isinstance(usage_raw, dict):
        usage_raw = {}
    input_tokens = _coerce_int(usage_raw.get("input_tokens"))
    output_tokens = _coerce_int(usage_raw.get("output_tokens"))
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
