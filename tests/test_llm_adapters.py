from models_pipeline.llm.backends.anthropic import (
    _extract_response as anthropic_extract,
)
from models_pipeline.llm.backends.openai import _extract_response as openai_extract


def test_openai_extract_response_reads_content() -> None:
    payload = {
        "choices": [
            {
                "message": {"role": "assistant", "content": "hello from openai"},
                "finish_reason": "stop",
            }
        ],
        "usage": {"prompt_tokens": 10, "completion_tokens": 5, "total_tokens": 15},
    }
    response = openai_extract(payload, "demo-model", "https://example.com/v1")
    assert response.content == "hello from openai"
    assert response.usage == {
        "input_tokens": 10,
        "output_tokens": 5,
        "total_tokens": 15,
    }


def test_anthropic_extract_response_reads_text_blocks() -> None:
    payload = {
        "content": [{"type": "text", "text": "hello"}],
        "usage": {"input_tokens": 2, "output_tokens": 3},
        "stop_reason": "end_turn",
    }
    response = anthropic_extract(payload, "claude-3", "https://api.anthropic.com")
    assert response.content == "hello"
    assert response.usage == {"input_tokens": 2, "output_tokens": 3, "total_tokens": 5}
