import re
from datetime import datetime, timezone
from pathlib import Path


def slugify(value: str) -> str:
    slug = re.sub(r"[^A-Za-z0-9._-]+", "_", value).strip("._-")
    return slug or "item"


def create_run_dir(base_dir: Path) -> Path:
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    run_dir = base_dir / stamp
    if run_dir.exists():
        suffix = 1
        while (base_dir / f"{stamp}_{suffix}").exists():
            suffix += 1
        run_dir = base_dir / f"{stamp}_{suffix}"
    run_dir.mkdir(parents=True, exist_ok=False)
    return run_dir


def utc_iso() -> str:
    return datetime.now(timezone.utc).isoformat()
