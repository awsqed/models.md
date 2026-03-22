"""Prompt helpers for source summarization."""

import re

from models_pipeline.prompt._render import join_prompt_sections

MAX_CRITICAL_ITEMS = 25
MAX_CRITICAL_ITEM_LENGTH = 120

CRITICAL_PATTERNS = (
    re.compile(r"https?://\S+"),
    re.compile(r"\b[a-f0-9]{8,}\b", re.IGNORECASE),
    re.compile(
        r"\b(?:gpt|claude|gemini|llama|glm|qwen|mistral|copilot|opencode)[\w./:-]*\b",
        re.IGNORECASE,
    ),
    re.compile(r"^\s*[A-Za-z0-9_.-]+\s*:", re.MULTILINE),
)

SUMMARY_SYSTEM_PROMPT = """You compress source material for a downstream catalog-generation pipeline.
Preserve critical factual context exactly.
Return only the summary text with no preamble, commentary, or code fences."""

SUMMARY_REQUIREMENTS = (
    "- Preserve provider names, model names, model ids, aliases, status/eol/replacement facts, URLs, API endpoints, version markers, and dates exactly.",
    "- For models.dev API records: preserve id, provider_id, context/input/output limits, cost, reasoning, tool_call, release_date, and knowledge cutoff. Omit name, family, open_weights, modalities detail, last_updated, and attachment unless they are the only differentiator needed to disambiguate records.",
    "- Preserve tables, bullet lists, and heading structure when they carry provider/model information.",
    "- Remove boilerplate, marketing copy, repeated explanations, and unrelated narrative.",
    "- Keep uncertain facts out; do not infer or normalize beyond what the source states.",
    "- If a section is relevant, compress it but keep concrete facts intact.",
    "- Output plain text/markdown only, with no commentary about the summarization process.",
)


def build_summary_prompt(source_name: str, text: str) -> tuple[str, str]:
    critical_items = _extract_critical_items(text)
    source_specific_requirements = _source_specific_requirements(source_name)
    requirements = [*SUMMARY_REQUIREMENTS, *source_specific_requirements]
    user_prompt = join_prompt_sections(
        [
            f"Source name: {source_name}",
            "Task: summarize this source for a downstream model/provider catalog pipeline.",
            "Requirements:",
            *requirements,
            "Critical items detected:\n- "
            + "\n- ".join(critical_items if critical_items else ["none detected"]),
            "Source text:\n" + text,
        ]
    )
    return SUMMARY_SYSTEM_PROMPT, user_prompt


def _extract_critical_items(text: str) -> list[str]:
    items: list[str] = []
    seen: set[str] = set()
    for match in _iter_pattern_matches(text):
        value = _truncate(match.strip(), MAX_CRITICAL_ITEM_LENGTH)
        if value and value not in seen:
            seen.add(value)
            items.append(value)
        if len(items) >= MAX_CRITICAL_ITEMS:
            return items
    return items


def _iter_pattern_matches(text: str):
    for pattern in CRITICAL_PATTERNS:
        for match in pattern.findall(text):
            if isinstance(match, tuple):
                value = next((group for group in match if group), "")
            else:
                value = match
            if value:
                yield value


def _truncate(value: str, max_len: int) -> str:
    if len(value) <= max_len:
        return value
    return value[: max_len - 3] + "..."


def _source_specific_requirements(source_name: str) -> tuple[str, ...]:
    if source_name != "models_dev_api":
        return ()
    return (
        "- For models_dev_api specifically, prefer one compact bullet per model; do not emit per-field bullet lists.",
        "- models_dev_api compact format: `id=<id> | provider_id=<provider> | limit=ctx:<n>,in:<n>,out:<n> | cost=in:<x>,out:<x> | reasoning=<bool> | tool_call=<bool> | rel=<date> | knowledge=<value>`.",
        "- For models_dev_api specifically, drop `name`, `family`, `modalities`, and other descriptive fields unless needed to distinguish otherwise identical ids.",
    )
