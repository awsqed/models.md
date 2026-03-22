import sys
from pathlib import Path

from models_pipeline import cli


def test_parse_args_accepts_minimal_cli(monkeypatch) -> None:
    root = Path(__file__).resolve().parents[1]
    if str(root) not in sys.path:
        sys.path.insert(0, str(root))
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "models-pipeline",
            "--sources",
            "custom.json",
            "--model",
            "summary-model",
            "--api-base-url",
            "https://example.com/v1",
            "--check",
        ],
    )

    args = cli.parse_args()

    assert args.sources == "custom.json"
    assert args.model == "summary-model"
    assert args.api_base_url == "https://example.com/v1"
    assert args.check is True


def test_parse_args_accepts_until_step(monkeypatch) -> None:
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "models-pipeline",
            "--sources",
            "custom.json",
            "--until-step",
            "build_prompt",
        ],
    )

    args = cli.parse_args()

    assert args.sources == "custom.json"
    assert args.until_step == "build_prompt"
