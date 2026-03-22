"""Build prompts fed to LLM backends."""

import re

from models_pipeline.prompt._render import join_prompt_sections, render_bullet_block

CATALOG_SYSTEM_PROMPT = (
    "You maintain a sharded AI model catalog. "
    "Return only a single JSON object mapping output file names to their full markdown content. "
    "Every output file listed in the rules must appear as a key. "
    "Every file's content must be complete - do not truncate, summarize, or omit any section. "
    "Your response must be valid JSON parseable by Python's json.loads(). "
    'Ensure all string values properly escape newlines as \\n, quotes as \\" and backslashes as \\\\. '
    "Do not include code fences, commentary, preambles, or thinking traces. "
    "Your response must start with '{' and end with '}'."
)

SKELETON_SOURCE_NAMES = {
    "copilot_catalog",
    "opencode_catalog",
    "lifecycle",
    "views",
}
HEADING_RE = re.compile(r"^\s{0,3}#{1,3}\s")
METADATA_COMMENT_RE = re.compile(r"^\s*>\s")


def build_catalog_prompt(
    source_blobs: list[tuple[str, str]],
    schema_text: str,
    output_names: list[str],
) -> tuple[str, str]:
    """Return (system_prompt, user_prompt) for catalog regeneration."""
    sections = [
        "You are given schema and sources. Regenerate outputs.",
        render_bullet_block("Rules:", _catalog_rules(output_names)),
        "Schema:\n" + schema_text,
    ]
    for name, blob in source_blobs:
        source_blob = _skeletonize(blob) if name in SKELETON_SOURCE_NAMES else blob
        sections.append(f"Source: {name}\n{source_blob}")
    return CATALOG_SYSTEM_PROMPT, join_prompt_sections(sections)


def _catalog_rules(output_names: list[str]) -> list[str]:
    rules = [
        f"Output exactly these {len(output_names)} keys: {', '.join(output_names)}.",
        "Each key's value must be the complete markdown content for that file - no truncation.",
        "Preserve all model IDs, provider names, aliases, status values, EOL dates, and replacement references exactly as found in sources.",
        "Preserve normalized short-id format.",
        "Catalog source skeletons are provided for structural reference only - regenerate full content from all sources.",
        "Do not output analysis; output only the final JSON object.",
    ]
    if "docs/models/models.lifecycle.md" in output_names:
        rules.append(
            "docs/models/models.lifecycle.md must be derived from catalog statuses/eol/repl fields only."
        )
    if "docs/models/models.views.md" in output_names:
        rules.append(
            "docs/models/models.views.md must exclude retired models and models retiring within 30 days of document_date."
        )
    return rules


def _skeletonize(blob: str) -> str:
    skeleton_lines: list[str] = []
    for line in blob.splitlines():
        if HEADING_RE.match(line):
            skeleton_lines.append(line)
            continue
        if METADATA_COMMENT_RE.match(line):
            skeleton_lines.append(line)
    return "\n".join(skeleton_lines)
