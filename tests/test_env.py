import os
from pathlib import Path

from models_pipeline.env import load_workspace_env


def test_load_workspace_env_reads_root_dotenv(tmp_path: Path, monkeypatch) -> None:
    env_path = tmp_path / ".env"
    env_path.write_text("OPENAI_API_KEY=from-dotenv\n", encoding="utf-8")
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)

    loaded = load_workspace_env(tmp_path)

    assert loaded == env_path
    assert os.environ["OPENAI_API_KEY"] == "from-dotenv"


def test_load_workspace_env_preserves_existing_values(
    tmp_path: Path, monkeypatch
) -> None:
    env_path = tmp_path / ".env"
    env_path.write_text("OPENAI_API_KEY=from-dotenv\n", encoding="utf-8")
    monkeypatch.setenv("OPENAI_API_KEY", "existing")

    load_workspace_env(tmp_path)

    assert os.environ["OPENAI_API_KEY"] == "existing"
