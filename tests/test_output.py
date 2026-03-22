from pathlib import Path

import pytest
from models_pipeline import output

ALLOWED_OUTPUTS = [
    "docs/models/models.catalog.md",
    "docs/models/models.lifecycle.md",
]


def _outputs() -> dict[str, str]:
    return {name: f"# {Path(name).name}\n" for name in ALLOWED_OUTPUTS}


def test_parse_requires_all_outputs() -> None:
    raw = '{"docs/models/models.catalog.md": "# one"}'

    with pytest.raises(ValueError, match="missing output files"):
        output.parse(raw, ALLOWED_OUTPUTS)


def test_write_or_check_validates_extra_outputs(tmp_path: Path) -> None:
    bad_outputs = _outputs() | {"docs/models/extra.md": "# bad\n"}

    with pytest.raises(ValueError, match="Unexpected output files"):
        output.validate(bad_outputs, ALLOWED_OUTPUTS)


def test_write_or_check_updates_only_given_outputs(tmp_path: Path) -> None:
    outputs = _outputs()

    assert output.write_or_check(outputs, root=tmp_path, check=False) is True
    assert (
        (tmp_path / "docs/models/models.catalog.md")
        .read_text(encoding="utf-8")
        .startswith("# models.catalog.md")
    )


def test_write_or_check_detects_out_of_date_in_check_mode(tmp_path: Path) -> None:
    outputs = _outputs()
    path = tmp_path / "docs/models/models.catalog.md"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("# stale\n", encoding="utf-8")

    ok = output.write_or_check(outputs, root=tmp_path, check=True)

    assert ok is False
