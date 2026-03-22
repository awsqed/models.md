import argparse
from pathlib import Path

from models_pipeline.env import load_workspace_env
from models_pipeline.pipeline import PIPELINE_STEP_ORDER, PipelineOptions, run

DEFAULT_SOURCES_FILE = Path(__file__).resolve().parents[2] / "config.json"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Regenerate AI model catalog markdown files using an LLM.",
    )
    parser.add_argument(
        "--sources",
        default=str(DEFAULT_SOURCES_FILE),
        metavar="PATH",
        help="Path to JSON source config (default: config.json).",
    )
    parser.add_argument(
        "--model",
        default="",
        metavar="MODEL",
        help="Override the model specified in the config file.",
    )
    parser.add_argument(
        "--api-base-url",
        default="",
        metavar="URL",
        help="OpenAI-compatible API base URL (overrides config).",
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="Validate outputs without writing files (CI mode).",
    )
    parser.add_argument(
        "--until-step",
        default="",
        choices=PIPELINE_STEP_ORDER,
        metavar="STEP",
        help=(
            "Run pipeline only through STEP (inclusive). "
            "Executes all prerequisite steps in order."
        ),
    )
    return parser.parse_args()


def main() -> int:
    root = Path(__file__).resolve().parents[2]
    load_workspace_env(root)
    args = parse_args()
    options = PipelineOptions(
        config_path=Path(args.sources),
        model_override=args.model,
        api_base_url_override=args.api_base_url,
        check=args.check,
        until_step=args.until_step,
    )
    return run(options, root=root)
