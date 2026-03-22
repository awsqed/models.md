import socket

from openai import APIConnectionError, APIStatusError, APITimeoutError, OpenAI

from models_pipeline.llm.errors import LLMFatalError, LLMRetryableError
from models_pipeline.llm.types import ChatRequest, ChatResponse

_RETRYABLE_STATUS_CODES = {408, 429, 500, 502, 503, 504}


def _normalize_base_url(raw: str) -> str:
    base = raw.strip().rstrip("/")
    if base.endswith("/chat/completions"):
        base = base[: -len("/chat/completions")].rstrip("/")
    return base


class OpenAIBackend:
    def complete(self, request: ChatRequest, api_key: str) -> ChatResponse:
        base_url = _normalize_base_url(request.api_base_url)
        client = OpenAI(
            api_key=api_key,
            base_url=base_url,
            timeout=float(request.timeout_seconds),
            max_retries=0,
        )

        body: dict[str, object] = {
            "model": request.model,
            "temperature": 0,
            "messages": [
                {"role": m.role, "content": m.content} for m in request.messages
            ],
        }
        if request.max_output_tokens is not None:
            body["max_tokens"] = request.max_output_tokens

        create_kwargs = dict(body)
        reasoning_extra: dict[str, object] | None = None
        if not request.reasoning:
            reasoning_extra = {"reasoning": {"enabled": False}}
        if reasoning_extra is not None:
            create_kwargs["extra_body"] = reasoning_extra

        try:
            completion = client.chat.completions.create(**create_kwargs)  # type: ignore
        except APIStatusError as exc:
            status = exc.status_code
            detail = str(exc.body) if exc.body is not None else str(exc)
            msg = (
                f"LLM API error {status} for model '{request.model}' "
                f"at {base_url}: {detail}"
            )
            if status in _RETRYABLE_STATUS_CODES:
                raise LLMRetryableError(msg, status_code=status) from exc
            if status == 400 and not request.reasoning and reasoning_extra is not None:
                try:
                    clean_kwargs = dict(create_kwargs)
                    clean_kwargs.pop("extra_body", None)
                    completion = client.chat.completions.create(**clean_kwargs)  # type: ignore
                except APIStatusError as exc2:
                    detail2 = str(exc2.body) if exc2.body is not None else str(exc2)
                    raise LLMFatalError(
                        f"LLM API error {exc2.status_code} for model '{request.model}' "
                        f"at {base_url}: {detail2}",
                        status_code=exc2.status_code,
                    ) from exc2
            else:
                raise LLMFatalError(msg, status_code=status) from exc
        except (APITimeoutError, TimeoutError, socket.timeout) as exc:
            raise LLMRetryableError(
                f"LLM request timed out for model '{request.model}' at {base_url} "
                f"after {request.timeout_seconds}s"
            ) from exc
        except APIConnectionError as exc:
            reason = exc.__cause__ if exc.__cause__ is not None else exc
            is_timeout = isinstance(reason, (TimeoutError, socket.timeout)) or (
                "timed out" in str(reason).lower()
            )
            error_cls = LLMRetryableError if is_timeout else LLMFatalError
            raise error_cls(
                f"LLM network error for model '{request.model}' at {base_url}: {reason}"
            ) from exc

        payload = completion.model_dump(mode="json")
        return _extract_response(payload, request.model, base_url)


def _extract_response(
    payload: dict[str, object], model: str, endpoint: str
) -> ChatResponse:
    choices = payload.get("choices")
    if not isinstance(choices, list) or not choices:
        raise LLMFatalError(
            f"LLM API returned no choices from model '{model}' at {endpoint}"
        )

    first = choices[0]
    if not isinstance(first, dict):
        raise LLMFatalError(f"LLM API returned malformed choice from model '{model}'")

    message = first.get("message") or {}
    if not isinstance(message, dict):
        message = {}

    content = _flatten_text(message.get("content"))
    if not content:
        for key in ("text", "output_text"):
            content = _flatten_text(message.get(key))
            if content:
                break
    if not content:
        reasoning_content = _flatten_text(message.get("reasoning_content"))
        if reasoning_content:
            stripped = reasoning_content.lstrip()
            if stripped.startswith("{") or stripped.startswith("```"):
                content = reasoning_content

    finish_reason = str(first.get("finish_reason", "")).strip().lower()
    if finish_reason in {"length", "max_tokens"}:
        raise LLMFatalError(
            f"LLM response truncated (finish_reason={finish_reason!r}, "
            f"content_chars={len(content)}). Increase max_output_tokens or reduce prompt size."
        )
    if not content:
        raise LLMFatalError(
            f"LLM API returned empty content (finish_reason={first.get('finish_reason')!r}, "
            f"message_keys={sorted(message.keys())})"
        )

    usage_raw = payload.get("usage") or {}
    if not isinstance(usage_raw, dict):
        usage_raw = {}
    usage = {
        "input_tokens": _coerce_int(usage_raw.get("prompt_tokens")),
        "output_tokens": _coerce_int(usage_raw.get("completion_tokens")),
        "total_tokens": _coerce_int(usage_raw.get("total_tokens")),
    }
    return ChatResponse(content=content, usage=usage)


def _flatten_text(value: object) -> str:
    if isinstance(value, str):
        return value
    if not isinstance(value, list):
        return ""
    chunks: list[str] = []
    for part in value:
        if isinstance(part, str):
            chunks.append(part)
        elif isinstance(part, dict):
            for key in ("text", "content", "output_text", "value"):
                text = part.get(key)
                if isinstance(text, str) and text:
                    chunks.append(text)
                    break
    return "".join(chunks)


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
