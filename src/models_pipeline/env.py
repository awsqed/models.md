from pathlib import Path

from dotenv import load_dotenv


def load_workspace_env(root: Path) -> Path:
    env_path = root / ".env"
    load_dotenv(env_path, override=False)
    return env_path
