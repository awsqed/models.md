from typing import Protocol

from models_pipeline.llm.types import ChatRequest, ChatResponse


class Backend(Protocol):
    def complete(self, request: ChatRequest, api_key: str) -> ChatResponse: ...
