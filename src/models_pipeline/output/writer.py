"""Write or check output markdown files."""

import sys
from pathlib import Path

from models_pipeline.output.validator import validate


def write_or_check(outputs: dict[str, str], *, root: Path, check: bool = False) -> bool:
    validate(outputs, list(outputs))
    ok = True
    for name in sorted(outputs):
        path = root / name
        current = path.read_text(encoding="utf-8") if path.exists() else ""
        expected = outputs[name]
        if current == expected:
            print(f"[output] up-to-date   {name}")
            continue
        if check:
            print(f"[output] OUT-OF-DATE  {name}", file=sys.stderr)
            ok = False
        else:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(expected, encoding="utf-8")
            print(f"[output] updated      {name}")
    return ok
