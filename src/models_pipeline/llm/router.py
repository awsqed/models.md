import os

from models_pipeline.llm.backend import Backend
from models_pipeline.llm.backends.anthropic import AnthropicBackend
from models_pipeline.llm.backends.gemini import GeminiBackend
from models_pipeline.llm.backends.openai import OpenAIBackend
from models_pipeline.llm.types import ChatRequest

_DEFAULT_KEY_ENV: dict[str, str] = {
    "anthropic": "ANTHROPIC_API_KEY",
    "gemini": "GEMINI_API_KEY",
    "openai": "OPENAI_API_KEY",
}


def _detect_provider(api_base_url: str) -> str:
    lowered = api_base_url.strip().lower()
    if "anthropic.com" in lowered:
        return "anthropic"
    if "googleapis.com" in lowered or "generativelanguage" in lowered:
        return "gemini"
    return "openai"


def resolve_backend(request: ChatRequest) -> tuple[Backend, str]:
    """Return (backend, api_key) for the given request."""
    provider = _detect_provider(request.api_base_url)

    key_env = request.api_key_env or _DEFAULT_KEY_ENV[provider]
    api_key = os.getenv(key_env, "").strip()
    if not api_key:
        raise RuntimeError(f"{key_env} is required")

    backend: Backend
    if provider == "anthropic":
        backend = AnthropicBackend()
    elif provider == "gemini":
        backend = GeminiBackend()
    else:
        backend = OpenAIBackend()

    return backend, api_key
