import time

from models_pipeline.llm.errors import LLMFatalError, LLMRetryableError
from models_pipeline.llm.router import resolve_backend
from models_pipeline.llm.types import ChatRequest, ChatResponse


def request_chat_completion(request: ChatRequest) -> ChatResponse:
    if request.timeout_seconds <= 0:
        raise ValueError("timeout_seconds must be >= 1")
    if request.max_retries < 0:
        raise ValueError("max_retries must be >= 0")
    if request.max_output_tokens is not None and request.max_output_tokens <= 0:
        raise ValueError("max_output_tokens must be >= 1 when provided")

    backend, api_key = resolve_backend(request)
    total_attempts = request.max_retries + 1

    for attempt in range(1, total_attempts + 1):
        try:
            return backend.complete(request, api_key)
        except LLMRetryableError as exc:
            if attempt < total_attempts:
                time.sleep(float(attempt))
                continue
            raise RuntimeError(
                f"LLM request failed after {total_attempts} attempt(s): {exc}"
            ) from exc
        except LLMFatalError as exc:
            raise RuntimeError(str(exc)) from exc

    raise RuntimeError("LLM request failed without a response")
