---
name: add-source-type
description: Guide for adding a new `sources[].type` in `config.json` with registry-driven parsing, validation, and tests.
---

Use this skill when introducing a new `sources[].type` in `config.json`.

## Goal

Add a source type with minimal coupling:

- source type is discovered through the parser registry
- parsing and validation logic is isolated in a dedicated parser
- loader, pipeline validation, and reader dispatch work without hardcoded edits

## Required implementation path

1. Add parser implementation in `src/models_pipeline/sources/parsers.py`
   - implement `SourceParser`
   - define:
     - `supported_kind`
     - `validate(self, item: SourceItem) -> None`
     - `parse(self, item: SourceItem, *, root: Path) -> str`
   - set `requires_crawl_support` only if crawl runtime is required

2. Register parser in `src/models_pipeline/sources/registry.py`
   - add `registry.register(YourSourceParser())` in `build_default_registry()`

3. Update config parsing only if necessary
   - `src/models_pipeline/config/loader.py` should stay registry-driven for kind validation
   - only add loader logic when new source needs special value coercion or config fields

4. Add tests
   - `tests/test_sources.py`
     - parser validation behavior
     - parse behavior
     - integration through `read(...)`
   - `tests/test_config.py` (if loader behavior changes)
   - `tests/test_pipeline.py` (if runtime prerequisites or step behavior changes)

5. Validate
   - run `make qa`

## Parser skeleton

```python
from pathlib import Path

from models_pipeline.config.schema import SourceItem
from models_pipeline.sources.base import SourceParser


class ExampleSourceParser(SourceParser):
    @property
    def supported_kind(self) -> str:
        return "example"

    def validate(self, item: SourceItem) -> None:
        if not isinstance(item.value, str):
            raise ValueError(f"example source expects string value: {item.name!r}")

    def parse(self, item: SourceItem, *, root: Path) -> str:
        del root
        return item.value
```

## Do / Don't

- Do keep source-specific logic inside parser classes.
- Do keep error messages explicit and actionable.
- Do preserve truncation behavior in `sources/reader.py` (post-parse).
- Don't add hardcoded allowed-kind sets in loader or pipeline steps.
