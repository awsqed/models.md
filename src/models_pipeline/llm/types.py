from dataclasses import dataclass


@dataclass(frozen=True)
class ChatMessage:
    role: str
    content: str


@dataclass(frozen=True)
class ChatRequest:
    model: str
    api_base_url: str
    messages: list[ChatMessage]
    timeout_seconds: int = 300
    max_retries: int = 2
    max_output_tokens: int | None = None
    reasoning: bool = False
    api_key_env: str | None = None  # None = auto-detect per backend


@dataclass(frozen=True)
class ChatResponse:
    content: str
    usage: dict[str, int]
