import json
from typing import Any

from models_pipeline.sources import fetch_models_dev_catalog


class _Response:
    def __init__(self, payload: str):
        self._payload = payload.encode("utf-8")

    def read(self) -> bytes:
        return self._payload

    def __enter__(self) -> "_Response":
        return self

    def __exit__(self, *_args: object) -> None:
        return None


def test_fetch_models_dev_catalog_filters_providers(monkeypatch) -> None:
    payload: dict[str, Any] = {
        "github-copilot": {
            "models": {"gpt-4.1": {"id": "gpt-4.1", "status": "active"}}
        },
        "opencode-go": {"models": {"glm-5": {"id": "glm-5", "status": "active"}}},
    }

    def fake_urlopen(_request: object, timeout: int) -> _Response:
        assert timeout == 60
        return _Response(json.dumps(payload))

    monkeypatch.setattr("urllib.request.urlopen", fake_urlopen)
    result = fetch_models_dev_catalog(providers=["github-copilot"])
    rows = json.loads(result)
    assert len(rows) == 1
    assert rows[0]["provider_id"] == "github-copilot"
    assert rows[0]["id"] == "gpt-4.1"
