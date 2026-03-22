import pytest
from models_pipeline.sources.registry import get_source_registry, SourceParserRegistry


def test_source_registry_has_builtin_kinds() -> None:
    kinds = set(get_source_registry().supported_kinds())
    assert kinds == {"file", "url", "text", "models_dev_api"}


def test_source_registry_rejects_duplicate_kind_registration() -> None:
    registry = SourceParserRegistry()
    parser = get_source_registry().get("text")
    registry.register(parser)
    with pytest.raises(ValueError, match="already registered"):
        registry.register(parser)
