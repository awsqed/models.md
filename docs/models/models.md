# AI Model Index

> updated: 2026-03-21
> role: read this file first
> schema: models.schema.yaml
> format: sharded, normalized, LLM-oriented

## Read Routing

- `billing, platform economics, file routing -> models.md`
- `raw GitHub Copilot records -> models.catalog.copilot.md`
- `raw OpenCode Go records -> models.catalog.opencode.md`
- `retired, retiring, replacement lookup -> models.lifecycle.md`
- `quick recommendations by cost, task, workflow -> models.views.md`
- `field meanings, aliases, normalization rules -> models.schema.yaml`
- `cross-platform compare -> read only the needed catalog shard(s) plus models.views.md; avoid loading every file unless you need exhaustive coverage`

## File Map

- `models.catalog.copilot.md`: normalized GitHub Copilot catalog
- `models.catalog.opencode.md`: normalized OpenCode Go catalog
- `models.lifecycle.md`: generated retirement and replacement map
- `models.views.md`: generated quick-pick summaries excluding retired and near-term retiring models
- `models.schema.yaml`: canonical field and normalization spec
- `models-pipeline` (`src/models_pipeline/cli.py`): LLM pipeline entrypoint and `--check` validator for derived files
- `config.json`: source list for local and external inputs

## Platform Billing

- `github-copilot`: premium request multiplier against monthly seat allowance; sub-agents and tool calls inside one session do not add extra cost beyond the initial request
- `opencode-go`: shared dollar pool `$12/5hr | $30/week | $60/month`; every sub-agent call consumes the pool
- `note`: Copilot through OpenCode TUI usually preserves more project context and follows instructions more faithfully than the official VS Code extension

## Record Format

- `id`: short model id; platform, vendor, and family come from the current file and headings
- `order`: `id | st | rel | eol | repl | ctx | out | in | rsn | tools | img | aud | vid | att | temp | mult | est | rate | best | sig | caut | fb`
- `st`: `active | preview | deprecated | retiring | retired | unconfirmed`
- `rsn`: `none | basic | 4k | low-med-high | low-med-high-xhigh | interleaved`
- `tools/img/aud/vid/att/temp`: `y | n | var | unk`
- `mult`: Copilot premium multiplier
- `est`: estimated OpenCode Go cost per request
- `best/sig/caut/fb`: primary use, differentiators, risks, fallback or migration target
- `full definitions -> models.schema.yaml`

## Derived Files

- `setup -> uv sync && uv run crawl4ai-setup`
- `generate -> OPENAI_API_KEY=... uv run models-pipeline --sources config.json`
- `validate -> OPENAI_API_KEY=... uv run models-pipeline --sources config.json --check`
- `retired models and models retiring within 30 days are excluded from docs/models/models.views.md`
