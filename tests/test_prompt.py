from models_pipeline.prompt import build_catalog_prompt, build_summary_prompt


def test_build_catalog_prompt_uses_caller_output_names() -> None:
    system, user = build_catalog_prompt(
        source_blobs=[("seed", "body")],
        schema_text="schema",
        output_names=["docs/models/custom-a.md", "docs/models/models.lifecycle.md"],
    )
    assert "Return only a single JSON object mapping output file names" in system
    assert "docs/models/custom-a.md, docs/models/models.lifecycle.md" in user
    assert "Source: seed" in user


def test_build_summary_prompt_includes_source_context() -> None:
    system, user = build_summary_prompt("source-a", "Model: gpt-4.1")
    assert "You compress source material" in system
    assert "Source name: source-a" in user
    assert "gpt-4.1" in user


def test_build_summary_prompt_includes_models_dev_api_requirement() -> None:
    _, user = build_summary_prompt("models_dev_api", "id: gpt-4.1")
    assert "For models.dev API records: preserve id, provider_id" in user
    assert "knowledge cutoff" in user
    assert "models_dev_api compact format" in user


def test_build_catalog_prompt_skeletonizes_catalog_sources() -> None:
    blob = (
        "# Top\n"
        "keep text? no\n"
        "## Section\n"
        "> source: meta\n"
        "- bullet dropped\n"
        "`id=model-a` provider=foo\n"
    )
    _, user = build_catalog_prompt(
        source_blobs=[("copilot_catalog", blob), ("seed", "plain body")],
        schema_text="schema",
        output_names=["docs/models/custom-a.md"],
    )

    assert "Source: copilot_catalog\n# Top\n## Section\n> source: meta" in user
    assert "keep text? no" not in user
    assert "- bullet dropped" not in user
    assert "`id=model-a` provider=foo" not in user
    assert "Source: seed\nplain body" in user


def test_build_catalog_prompt_includes_skeleton_rule() -> None:
    _, user = build_catalog_prompt(
        source_blobs=[],
        schema_text="schema",
        output_names=["docs/models/custom-a.md"],
    )
    assert "Catalog source skeletons are provided for structural reference only" in user
