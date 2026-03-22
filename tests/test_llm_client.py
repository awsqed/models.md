import pytest
from models_pipeline.llm import ChatMessage, ChatRequest, request_chat_completion
from models_pipeline.llm.backends.anthropic import AnthropicBackend
from models_pipeline.llm.backends.openai import OpenAIBackend
from models_pipeline.llm.errors import LLMFatalError, LLMRetryableError
from models_pipeline.llm.router import resolve_backend
from models_pipeline.llm.types import ChatResponse

# ── router tests ──────────────────────────────────────────────────────────────


def test_router_detects_anthropic_backend(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("ANTHROPIC_API_KEY", "sk-anthropic")
    backend, api_key = resolve_backend(
        ChatRequest(
            model="claude-3",
            api_base_url="https://api.anthropic.com/v1",
            messages=[],
        )
    )
    assert isinstance(backend, AnthropicBackend)
    assert api_key == "sk-anthropic"


def test_router_detects_openai_backend(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("OPENAI_API_KEY", "sk-openai")
    backend, api_key = resolve_backend(
        ChatRequest(
            model="gpt-4o",
            api_base_url="https://api.openai.com/v1",
            messages=[],
        )
    )
    assert isinstance(backend, OpenAIBackend)
    assert api_key == "sk-openai"


def test_router_respects_explicit_api_key_env(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("MY_CUSTOM_KEY", "custom-secret")
    backend, api_key = resolve_backend(
        ChatRequest(
            model="gpt-4o",
            api_base_url="https://some-proxy.example.com/v1",
            messages=[],
            api_key_env="MY_CUSTOM_KEY",
        )
    )
    assert api_key == "custom-secret"


def test_router_raises_if_api_key_missing(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    with pytest.raises(RuntimeError, match="OPENAI_API_KEY is required"):
        resolve_backend(
            ChatRequest(
                model="gpt-4o",
                api_base_url="https://api.openai.com/v1",
                messages=[],
            )
        )


# ── executor retry tests ───────────────────────────────────────────────────────


def test_executor_retries_on_retryable_error(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("OPENAI_API_KEY", "sk-test")
    attempt_count = 0

    class _FakeBackend:
        def complete(self, request: ChatRequest, api_key: str) -> ChatResponse:
            nonlocal attempt_count
            attempt_count += 1
            if attempt_count < 2:
                raise LLMRetryableError("rate limited", status_code=429)
            return ChatResponse(
                content="ok",
                usage={"input_tokens": 1, "output_tokens": 1, "total_tokens": 2},
            )

    monkeypatch.setattr(
        "models_pipeline.llm.executor.resolve_backend",
        lambda r: (_FakeBackend(), "sk-test"),
    )
    monkeypatch.setattr("models_pipeline.llm.executor.time.sleep", lambda s: None)

    response = request_chat_completion(
        ChatRequest(
            model="gpt-4o",
            api_base_url="https://api.openai.com/v1",
            messages=[ChatMessage(role="user", content="hi")],
            max_retries=2,
        )
    )
    assert response.content == "ok"
    assert attempt_count == 2


def test_executor_raises_after_max_retries(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("OPENAI_API_KEY", "sk-test")

    class _AlwaysFailBackend:
        def complete(self, request: ChatRequest, api_key: str) -> ChatResponse:
            raise LLMRetryableError("always fails", status_code=503)

    monkeypatch.setattr(
        "models_pipeline.llm.executor.resolve_backend",
        lambda r: (_AlwaysFailBackend(), "sk-test"),
    )
    monkeypatch.setattr("models_pipeline.llm.executor.time.sleep", lambda s: None)

    with pytest.raises(RuntimeError, match="3 attempt"):
        request_chat_completion(
            ChatRequest(
                model="gpt-4o",
                api_base_url="https://api.openai.com/v1",
                messages=[ChatMessage(role="user", content="hi")],
                max_retries=2,
            )
        )


def test_executor_does_not_retry_fatal_error(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("OPENAI_API_KEY", "sk-test")
    attempt_count = 0

    class _FatalBackend:
        def complete(self, request: ChatRequest, api_key: str) -> ChatResponse:
            nonlocal attempt_count
            attempt_count += 1
            raise LLMFatalError("invalid request", status_code=400)

    monkeypatch.setattr(
        "models_pipeline.llm.executor.resolve_backend",
        lambda r: (_FatalBackend(), "sk-test"),
    )

    with pytest.raises(RuntimeError, match="invalid request"):
        request_chat_completion(
            ChatRequest(
                model="gpt-4o",
                api_base_url="https://api.openai.com/v1",
                messages=[ChatMessage(role="user", content="hi")],
                max_retries=3,
            )
        )
    assert attempt_count == 1
