---
name: add-source-type
description: Guide for adding a new `sources[].type` in `config.json` with registry-driven parsing, validation, and tests.
---

# Add Source Type

## Overview

Use this skill when introducing a new `sources[].type` in `config.json`.

Add a source type with minimal coupling:

- source type is discovered through the parser registry
- parsing and validation logic is isolated in a dedicated parser
- loader, pipeline validation, and reader dispatch work without hardcoded edits

## Parser Skeleton

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

## Workflow

### 1. Add Parser Implementation

Implement a parser in `src/models_pipeline/sources/parsers.py`:

- implement `SourceParser`
- define:
   - `supported_kind`
   - `validate(self, item: SourceItem) -> None`
   - `parse(self, item: SourceItem, *, root: Path) -> str`
- set `requires_crawl_support` only if crawl runtime is required

### 2. Register Parser

Register the parser in `src/models_pipeline/sources/registry.py`:

- add `registry.register(YourSourceParser())` in `build_default_registry()`

### 3. Update Config Parsing Only If Needed

Update config parsing only if necessary:

- `src/models_pipeline/config/loader.py` should stay registry-driven for kind validation
- only add loader logic when new source needs special value coercion or config fields

### 4. Add Tests

Add tests:

- `tests/test_sources.py`
   - parser validation behavior
   - parse behavior
   - integration through `read(...)`
- `tests/test_config.py` (if loader behavior changes)
- `tests/test_pipeline.py` (if runtime prerequisites or step behavior changes)

### 5. Validate

Run validation:

- run `make qa`

## Best Practices

- Keep source-specific logic inside parser classes.
- Keep error messages explicit and actionable.
- Preserve truncation behavior in `sources/reader.py` (post-parse).
- Keep loader and pipeline validation registry-driven.

## Source Safety Protocol

- NEVER add hardcoded allowed-kind sets in loader or pipeline steps.
- NEVER bypass parser-level validation for a new source kind.
- ONLY set `requires_crawl_support` when crawl runtime is actually required.
