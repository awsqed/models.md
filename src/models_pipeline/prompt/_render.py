"""Shared helpers for assembling prompt sections."""

from collections.abc import Iterable


def join_prompt_sections(sections: Iterable[str]) -> str:
    return "\n\n".join(sections)


def prefix_lines(lines: Iterable[str], *, prefix: str = "- ") -> list[str]:
    return [f"{prefix}{line}" for line in lines]


def render_bullet_block(title: str, lines: Iterable[str], *, prefix: str = "- ") -> str:
    return f"{title}\n" + "\n".join(prefix_lines(lines, prefix=prefix))
