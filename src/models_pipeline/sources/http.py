"""HTTP helpers for JSON-backed pipeline sources."""

import json
import urllib.request
from typing import cast

MODELS_DEV_API_URL = "https://models.dev/api.json"
SUPPORTED_PROVIDER_KEYS = {"github-copilot", "opencode-go"}


def _load_json(url: str, *, timeout_seconds: int = 60) -> object:
    request = urllib.request.Request(
        url,
        headers={
            "Accept": "application/json",
            "User-Agent": "models-pipeline/1.0",
        },
        method="GET",
    )
    with urllib.request.urlopen(request, timeout=timeout_seconds) as response:
        return json.loads(response.read().decode("utf-8"))


def _extract_models(raw_provider: object, provider: str) -> list[dict[str, object]]:
    if isinstance(raw_provider, dict):
        provider_dict = cast(dict[str, object], raw_provider)
        raw_models = provider_dict.get("models")
        if isinstance(raw_models, dict):
            return [
                dict(cast(dict[str, object], model))
                for model in raw_models.values()
                if isinstance(model, dict)
            ]
        if isinstance(raw_models, list):
            return [
                dict(cast(dict[str, object], model))
                for model in raw_models
                if isinstance(model, dict)
            ]
    raise RuntimeError(
        f"models.dev API provider {provider!r} has no supported models payload"
    )


def fetch_models_dev_catalog(
    *,
    url: str = MODELS_DEV_API_URL,
    providers: list[str] | None = None,
    timeout_seconds: int = 60,
) -> str:
    """Fetch and normalize selected providers from models.dev API."""
    payload = _load_json(url, timeout_seconds=timeout_seconds)
    if not isinstance(payload, dict):
        raise RuntimeError("models.dev API returned a non-object payload")

    selected_providers = providers or sorted(SUPPORTED_PROVIDER_KEYS)
    result: list[dict[str, object]] = []
    for provider in selected_providers:
        raw_provider = payload.get(provider)
        models = _extract_models(raw_provider, provider)
        if not models:
            raise RuntimeError(
                f"models.dev API provider {provider!r} returned no models"
            )
        for model in models:
            entry = dict(model)
            entry["provider_id"] = provider
            result.append(entry)

    return json.dumps(result, ensure_ascii=False, indent=2) + "\n"
